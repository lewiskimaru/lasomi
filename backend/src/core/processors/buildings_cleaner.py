"""
Unified Buildings Cleaner

Source-specific building footprint cleaning with correct metric calculations and
minimal disruption to existing raw processing. This consolidates per-source
logic into a single module with clear strategies:

- Google Open Buildings: use provided area/confidence when available, compute
  metrics in meters, filter tiny polygons, deduplicate overlaps.
- Microsoft Building Footprints: placeholder (pass-through for now).
- OSM Buildings: clip strictly to AOI polygon to remove out-of-bound features.

Only geometry and diagnostic flags are modified; existing properties are
preserved. Cleaning is invoked explicitly by API (clean=true).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape as shapely_shape, Polygon, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree

from src.api.schemas_v2 import DataSourceType as DataSourceTypeV2
from src.api.api_schemas import DataSourceType as DataSourceTypeV1

logger = logging.getLogger(__name__)


@dataclass
class BuildingsCleanerConfig:
    # General thresholds
    min_area_m2: float = 8.0               # default tiny building cutoff
    overlap_threshold: float = 0.30        # 30% of smaller polygon
    edge_buffer_m: float = 0.5             # guard against edge-only overlaps
    strategy: str = "highest_confidence"   # or "largest_area" or "union"
    simplify_tolerance_m: Optional[float] = None
    make_valid: bool = True
    # Google-specific
    google_min_confidence: float = 0.65    # drop very low-confidence detections
    # Shape quality filters
    min_width_m: float = 2.0               # minimum morphological width (thickness)
    min_compactness: float = 0.08          # Polsby-Popper ~ 4πA/P^2
    max_elongation: float = 8.0            # max length/width ratio
    # OSM-specific (optional)
    osm_min_area_m2: float = 0.0           # if > 0, drop OSM buildings below this area (no clipping)


class BuildingsCleaner:
    """
    Orchestrates per-source building cleaning.
    """

    BUILDING_SOURCES_V2 = {
        DataSourceTypeV2.GOOGLE_BUILDINGS,
        DataSourceTypeV2.MICROSOFT_BUILDINGS,
        DataSourceTypeV2.OSM_BUILDINGS,
    }
    BUILDING_SOURCES_V1 = {
        DataSourceTypeV1.GOOGLE_BUILDINGS,
        DataSourceTypeV1.MICROSOFT_BUILDINGS,
        DataSourceTypeV1.OSM_BUILDINGS,
    }

    def clean(self, source_type: Any, feature_collection: Any, aoi_polygon_wgs84: Polygon, cfg: BuildingsCleanerConfig) -> Any:
        """
        Clean buildings per source. Returns a FeatureCollection with cleaned features.
        Non-building sources are returned unchanged.
        """
        try:
            if not self._is_building_source(source_type):
                return feature_collection

            if source_type in {DataSourceTypeV2.GOOGLE_BUILDINGS, DataSourceTypeV1.GOOGLE_BUILDINGS}:
                return self._clean_google(feature_collection, aoi_polygon_wgs84, cfg)
            elif source_type in {DataSourceTypeV2.MICROSOFT_BUILDINGS, DataSourceTypeV1.MICROSOFT_BUILDINGS}:
                return self._clean_microsoft(feature_collection, aoi_polygon_wgs84, cfg)
            else:
                # OSM Buildings
                return self._clean_osm(feature_collection, aoi_polygon_wgs84, cfg)
        except Exception:
            logger.exception("BuildingsCleaner.clean failed; returning original features")
            return feature_collection

    # ---------------------------- Google ----------------------------
    def _clean_google(self, feature_collection: Any, aoi_polygon_wgs84: Polygon, cfg: BuildingsCleanerConfig) -> Any:
        source_name = "google_buildings"
        gdf_wgs84 = self._feature_collection_to_gdf(feature_collection)
        original_count = len(gdf_wgs84)
        if gdf_wgs84.empty:
            return feature_collection

        logger.info(f"Cleaning {source_name}: {original_count} features")

        # Extract confidence/area_in_meters from properties if available
        if "confidence" not in gdf_wgs84.columns:
            gdf_wgs84["confidence"] = gdf_wgs84.apply(self._extract_confidence_from_props, axis=1)
        if "area_in_meters" not in gdf_wgs84.columns:
            gdf_wgs84["area_in_meters"] = gdf_wgs84.apply(self._extract_area_from_props, axis=1)

        # Compute metrics in meters using best-effort UTM zone from AOI
        utm_epsg = self._suggest_utm_epsg(aoi_polygon_wgs84) or 3857
        gdf_m = gdf_wgs84.set_crs(epsg=4326, allow_override=True).to_crs(epsg=utm_epsg)

        # Topology repair
        if cfg.make_valid:
            gdf_m["geometry"] = gdf_m.geometry.buffer(0)

        # Minimum confidence filter
        before_conf = len(gdf_m)
        gdf_m = gdf_m[gdf_m["confidence"].astype(float).fillna(0.0) >= float(cfg.google_min_confidence)].copy()
        after_conf = len(gdf_m)
        if before_conf - after_conf > 0:
            logger.info(f"{source_name}: removed {before_conf - after_conf} features below confidence {cfg.google_min_confidence}")

        # Minimum area filter (prefer property value if present)
        if cfg.min_area_m2 and cfg.min_area_m2 > 0:
            # Compute geometric area in meters
            geom_area = gdf_m.geometry.area
            # Choose best available: property area_in_meters if >0 else geometric
            eff_area = gdf_m.get("area_in_meters").astype(float).fillna(0.0)
            eff_area = eff_area.where(eff_area > 0, geom_area)
            before_area = len(gdf_m)
            gdf_m = gdf_m[eff_area >= float(cfg.min_area_m2)].copy()
            removed = before_area - len(gdf_m)
            if removed > 0:
                logger.info(f"{source_name}: removed {removed} < {cfg.min_area_m2}m²")

        if gdf_m.empty:
            return feature_collection

        # Shape-quality filters (metrics in meters)
        def _compactness(poly) -> float:
            try:
                p = poly.length
                a = poly.area
                if p <= 0:
                    return 0.0
                import math
                return (4 * math.pi * a) / (p * p)
            except Exception:
                return 0.0

        def _elongation(poly) -> float:
            try:
                mbr = poly.minimum_rotated_rectangle
                xs, ys = zip(*list(mbr.exterior.coords))
                # MBR has 5 points (closed). Compute side lengths
                sides = [((xs[i]-xs[i-1])**2 + (ys[i]-ys[i-1])**2)**0.5 for i in range(1, len(xs))]
                if not sides:
                    return 1.0
                length = max(sides)
                width = min(sides) if min(sides) > 0 else 1e-6
                return max(length/width, width/length)
            except Exception:
                return 1.0

        def _min_width(poly) -> float:
            # approximate by erosion until vanishing
            try:
                # Binary search on width using offsets
                low, high = 0.0, 20.0
                for _ in range(8):
                    mid = (low + high) / 2.0
                    if mid == 0:
                        low = mid
                        continue
                    shrunk = poly.buffer(-mid)
                    if shrunk.is_empty:
                        high = mid
                    else:
                        low = mid
                return low * 2.0  # approximate diameter (two-sided erosion)
            except Exception:
                return 0.0

        if not gdf_m.empty:
            # Compute quality metrics
            gdf_m["_compactness"] = gdf_m.geometry.apply(_compactness)
            gdf_m["_elongation"] = gdf_m.geometry.apply(_elongation)
            if cfg.min_width_m and cfg.min_width_m > 0:
                gdf_m["_min_width"] = gdf_m.geometry.apply(_min_width)
            else:
                gdf_m["_min_width"] = 9999.0

            before_shape = len(gdf_m)
            mask = (
                (gdf_m["_compactness"].fillna(0.0) >= float(cfg.min_compactness)) &
                (gdf_m["_elongation"].fillna(1.0) <= float(cfg.max_elongation)) &
                (gdf_m["_min_width"].fillna(0.0) >= float(cfg.min_width_m))
            )
            gdf_m = gdf_m[mask].copy()
            removed_shape = before_shape - len(gdf_m)
            if removed_shape > 0:
                logger.info(f"google_buildings: removed {removed_shape} by shape filters (width≥{cfg.min_width_m}m, compactness≥{cfg.min_compactness}, elongation≤{cfg.max_elongation})")

        # Deduplicate overlaps within source
        gdf_m = self._deduplicate_within_source(gdf_m, cfg)

        # Optional simplify
        if cfg.simplify_tolerance_m and cfg.simplify_tolerance_m > 0:
            gdf_m["geometry"] = gdf_m.geometry.simplify(cfg.simplify_tolerance_m, preserve_topology=True)

        cleaned_wgs84 = gdf_m.to_crs(epsg=4326)
        return self._gdf_to_feature_collection(cleaned_wgs84, template_fc=feature_collection)

    # ---------------------------- Microsoft ----------------------------
    def _clean_microsoft(self, feature_collection: Any, aoi_polygon_wgs84: Polygon, cfg: BuildingsCleanerConfig) -> Any:
        """Placeholder pass-through for now."""
        logger.info("Cleaning microsoft_buildings: pass-through (to be implemented)")
        return feature_collection

    # ---------------------------- OSM ----------------------------
    def _clean_osm(self, feature_collection: Any, aoi_polygon_wgs84: Polygon, cfg: BuildingsCleanerConfig) -> Any:
        """
        Buildings policy for OSM:
        - Drop features that do not intersect the AOI at all
        - Keep full geometry for features that intersect (do NOT clip/reshape)
        """
        from geojson_pydantic import FeatureCollection
        try:
            features = getattr(feature_collection, "features", None)
            if not features:
                return feature_collection

            gdf = self._feature_collection_to_gdf(feature_collection)
            if gdf.empty:
                return feature_collection

            aoi = gpd.GeoSeries([aoi_polygon_wgs84], crs="EPSG:4326").iloc[0]
            mask = gdf.set_crs(epsg=4326, allow_override=True).geometry.intersects(aoi)
            kept = gdf[mask].copy()

            # Optional OSM area filter in meters (no geometry clipping)
            if cfg.osm_min_area_m2 and cfg.osm_min_area_m2 > 0 and not kept.empty:
                utm_epsg = self._suggest_utm_epsg(aoi_polygon_wgs84) or 3857
                kept_m = kept.to_crs(epsg=utm_epsg)
                before = len(kept_m)
                kept_m = kept_m[kept_m.geometry.area >= float(cfg.osm_min_area_m2)].copy()
                removed = before - len(kept_m)
                if removed > 0:
                    logger.info(f"osm_buildings: removed {removed} < {cfg.osm_min_area_m2}m² (area filter)")
                kept = kept_m.to_crs(epsg=4326)

            logger.info(f"osm_buildings: kept {len(kept)} / {len(gdf)} within/intersecting AOI (no clipping)")
            return self._gdf_to_feature_collection(kept, template_fc=feature_collection)
        except Exception:
            logger.exception("OSM buildings filter failed; returning original")
            return feature_collection

    # ---------------------------- internals ----------------------------
    def _is_building_source(self, source_type: Any) -> bool:
        try:
            return source_type in self.BUILDING_SOURCES_V2 or source_type in self.BUILDING_SOURCES_V1
        except Exception:
            return False

    def _feature_collection_to_gdf(self, feature_collection: Any) -> gpd.GeoDataFrame:
        try:
            features = getattr(feature_collection, "features", None)
            if features is None:
                return gpd.GeoDataFrame(columns=["geometry"])  # empty
            records: List[Dict[str, Any]] = []
            for f in features:
                props = dict(getattr(f, "properties", {}) or {})
                geom = getattr(f, "geometry", None)
                if geom is None:
                    continue
                shapely_geom = shapely_shape(geom.dict()) if hasattr(geom, "dict") else shapely_shape(geom)
                records.append({**props, "geometry": shapely_geom})
            gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
            return gdf
        except Exception:
            logger.exception("_feature_collection_to_gdf failed")
            return gpd.GeoDataFrame(columns=["geometry"])  # empty

    def _gdf_to_feature_collection(self, gdf: gpd.GeoDataFrame, template_fc: Any) -> Any:
        from geojson_pydantic import Feature, FeatureCollection
        try:
            import math
            def _to_jsonable(v):
                try:
                    if hasattr(v, 'item'):
                        v = v.item()
                except Exception:
                    pass
                if isinstance(v, float):
                    return v if math.isfinite(v) else None
                if v is None:
                    return None
                if isinstance(v, (int, str, bool)):
                    return v
                return str(v)[:200]

            def _sanitize_props(d: dict) -> dict:
                return {k: _to_jsonable(v) for k, v in (d or {}).items()}

            features: List[Feature] = []
            for _, row in gdf.iterrows():
                props = {k: v for k, v in row.items() if k != "geometry"}
                props = _sanitize_props(props)
                geom_mapping = mapping(row.geometry)
                features.append(Feature(type="Feature", properties=props, geometry=geom_mapping))
            return FeatureCollection(type="FeatureCollection", features=features)
        except Exception:
            logger.exception("_gdf_to_feature_collection failed; returning template")
            return template_fc

    def _suggest_utm_epsg(self, aoi_wgs84: Polygon) -> Optional[int]:
        try:
            if aoi_wgs84 is None or aoi_wgs84.is_empty:
                return None
            lon, lat = aoi_wgs84.centroid.x, aoi_wgs84.centroid.y
            zone = int((lon + 180) // 6) + 1
            if lat >= 0:
                epsg = 32600 + zone
            else:
                epsg = 32700 + zone
            if 32601 <= epsg <= 32660 or 32701 <= epsg <= 32760:
                return epsg
            return None
        except Exception:
            return None

    def _extract_confidence_from_props(self, row: pd.Series) -> float:
        # Try direct property first
        val = row.get("confidence")
        try:
            if pd.notna(val):
                return float(val)
        except Exception:
            pass
        # Fallback: parse from description multi-line text
        desc = row.get("description")
        if isinstance(desc, str):
            for part in desc.split("\n"):
                if part.strip().lower().startswith("confidence:"):
                    try:
                        return float(part.split(":", 1)[1].strip())
                    except Exception:
                        continue
        return 1.0  # default if missing

    def _extract_area_from_props(self, row: pd.Series) -> Optional[float]:
        val = row.get("area_in_meters")
        try:
            if pd.notna(val):
                return float(val)
        except Exception:
            pass
        desc = row.get("description")
        if isinstance(desc, str):
            for part in desc.split("\n"):
                key = part.split(":", 1)[0].strip().lower()
                if key in {"area_in_meters", "area", "area_m2"}:
                    try:
                        return float(part.split(":", 1)[1].strip())
                    except Exception:
                        continue
        return None

    def _deduplicate_within_source(self, gdf_m: gpd.GeoDataFrame, cfg: BuildingsCleanerConfig) -> gpd.GeoDataFrame:
        if len(gdf_m) <= 1:
            return gdf_m
        geoms = list(gdf_m.geometry.values)
        tree = STRtree(geoms)
        index_by_geom = {id(geom): idx for idx, geom in enumerate(geoms)}

        visited: set[int] = set()
        groups: List[List[int]] = []

        for i, geom in enumerate(geoms):
            if i in visited:
                continue
            candidates = [index_by_geom.get(id(g)) for g in tree.query(geom)]
            candidates = [c for c in candidates if c is not None and c != i]
            current_group = [i]
            visited.add(i)
            for j in candidates:
                if j in visited:
                    continue
                if self._is_significant_overlap(geoms[i], geoms[j], cfg):
                    current_group.append(j)
                    visited.add(j)
            if len(current_group) > 1:
                groups.append(current_group)

        if not groups:
            return gdf_m

        to_drop: set[int] = set()
        union_rows: List[Dict[str, Any]] = []
        for group in groups:
            sub = gdf_m.iloc[group]
            if cfg.strategy == "largest_area":
                keep_idx = sub.geometry.area.idxmax()
                to_drop.update(set(group) - {keep_idx})
            elif cfg.strategy == "highest_confidence":
                if "confidence" in sub.columns:
                    try:
                        keep_idx = sub["confidence"].astype(float).idxmax()
                    except Exception:
                        keep_idx = sub.geometry.area.idxmax()
                else:
                    keep_idx = sub.geometry.area.idxmax()
                to_drop.update(set(group) - {keep_idx})
            elif cfg.strategy == "union":
                union_geom = unary_union(list(sub.geometry))
                rep = sub.iloc[0].drop(labels=["geometry"]).to_dict()
                if "confidence" in sub.columns:
                    try:
                        rep["confidence"] = float(sub["confidence"].astype(float).max())
                    except Exception:
                        pass
                union_rows.append({**rep, "geometry": union_geom, "source": "union"})
                to_drop.update(set(group))
            else:
                # default
                keep_idx = sub.geometry.area.idxmax()
                to_drop.update(set(group) - {keep_idx})

        cleaned = gdf_m.drop(index=to_drop).copy()
        if union_rows:
            union_gdf = gpd.GeoDataFrame(union_rows, geometry="geometry", crs=gdf_m.crs)
            cleaned = gpd.GeoDataFrame(pd.concat([cleaned, union_gdf], ignore_index=True), geometry="geometry", crs=gdf_m.crs)
        return cleaned

    def _is_significant_overlap(self, g1, g2, cfg: BuildingsCleanerConfig) -> bool:
        try:
            if cfg.edge_buffer_m and cfg.edge_buffer_m > 0:
                try:
                    b1 = g1.buffer(-cfg.edge_buffer_m)
                    b2 = g2.buffer(-cfg.edge_buffer_m)
                    if b1.is_empty or b2.is_empty or not b1.intersects(b2):
                        return False
                except Exception:
                    pass
            inter = g1.intersection(g2)
            if inter.is_empty:
                return False
            inter_area = getattr(inter, "area", 0.0) or 0.0
            if inter_area <= 0:
                return False
            a1 = getattr(g1, "area", 0.0) or 0.0
            a2 = getattr(g2, "area", 0.0) or 0.0
            smaller = min(a1, a2)
            if smaller <= 0:
                return False
            overlap_ratio = inter_area / smaller
            return overlap_ratio >= float(cfg.overlap_threshold)
        except Exception:
            return False
