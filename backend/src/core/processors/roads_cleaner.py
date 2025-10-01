"""
Roads Cleaner

Clips OSM roads to the AOI polygon (drops segments outside the AOI). This is
invoked when the API request sets clean_roads=true.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import geopandas as gpd
from shapely.geometry import Polygon, LineString, MultiLineString, mapping
from shapely.geometry import shape as shapely_shape
import math

logger = logging.getLogger(__name__)


@dataclass
class RoadsCleanerConfig:
    make_valid: bool = True


class RoadsCleaner:
    def clean_osm_roads(self, feature_collection: Any, aoi_polygon_wgs84: Polygon, cfg: RoadsCleanerConfig) -> Any:
        from geojson_pydantic import Feature, FeatureCollection
        try:
            features = getattr(feature_collection, "features", None)
            if not features:
                return feature_collection

            # Build GeoDataFrame
            records = []
            for f in features:
                props = dict(getattr(f, "properties", {}) or {})
                geom = getattr(f, "geometry", None)
                if not geom:
                    continue
                geom_obj = geom.dict() if hasattr(geom, "dict") else geom
                records.append({**props, "geometry": shapely_shape(geom_obj)})
            gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
            if gdf.empty:
                return feature_collection

            # Clip using geopandas.clip (handles LineString/MultiLineString vs Polygon)
            clipped = gpd.clip(gdf, aoi_polygon_wgs84)
            # Remove empty or null geometries that may result from clipping
            clipped = clipped[clipped.geometry.notnull() & ~clipped.geometry.is_empty].copy()
            logger.info(f"osm_roads: clipped {len(gdf)} → {len(clipped)} to AOI")

            # Convert back to FeatureCollection
            out_features = []
            def _to_jsonable(v):
                try:
                    # unwrap numpy scalar if present
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
                # Fallback: stringify short to avoid serialization errors
                return str(v)[:200]

            def _sanitize_props(d: dict) -> dict:
                return {k: _to_jsonable(v) for k, v in (d or {}).items()}

            for _, row in clipped.iterrows():
                props = {k: v for k, v in row.items() if k != "geometry"}
                props = _sanitize_props(props)
                geom_mapping = mapping(row.geometry)
                out_features.append(Feature(type="Feature", properties=props, geometry=geom_mapping))
            return FeatureCollection(type="FeatureCollection", features=out_features)
        except Exception:
            logger.exception("OSM roads clip failed; returning original")
            return feature_collection
