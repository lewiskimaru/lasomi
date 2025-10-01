# Research Links and Related Resources

https://github.com/suyash-bhosale/Building_Extraction_GEE_Code/tree/main

This file collects the research and tutorial links, grouped and annotated with a short description and suggested use. Use this as a quick reference when building connectors and for writing documentation.

---

## Google Open Buildings & Earth Engine

* [https://sites.research.google/gr/open-buildings/#open-buildings-download](https://sites.research.google/gr/open-buildings/#open-buildings-download)

  * Official Google Open Buildings project page. Primary landing page for dataset overview and download guidance.

* [https://developers.google.com/earth-engine/datasets/catalog/GOOGLE\_Research\_open-buildings\_v3\_polygons](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons)

  * Earth Engine dataset catalog entry for Open Buildings v3. Use this for programmatic access via the Earth Engine API; includes schema and properties.

* [https://sites.research.google/gr/open-buildings/temporal/](https://sites.research.google/gr/open-buildings/temporal/)

  * Temporal information and analysis related to Open Buildings releases — useful if you need historic versions or change-detection considerations.

---

## Extract boundary coordinates of an Area of Interest

* [https://arthur-e.github.io/Wicket/sandbox-gmaps3.html](https://arthur-e.github.io/Wicket/sandbox-gmaps3.html)

  * Wicket is a lightweight Javascript library that reads and writes Well-Known Text (WKT) strings. It can also be extended to parse and to create geometric objects from various mapping frameworks, such as Leaflet, the ESRI ArcGIS JavaScript API, and the Google Maps API.

---

## Tutorials, Notebooks, and How-to Guides (Open Buildings & related)

* [https://www.geodose.com/2023/08/how-to-download-google-microsoft-building-data.html](https://www.geodose.com/2023/08/how-to-download-google-microsoft-building-data.html)

  * Practical blog post explaining ways to download Google and Microsoft building footprints — good step-by-step guidance and tips for clipping and batching.

* [https://colab.research.google.com/github/google-research/google-research/blob/master/building\_detection/open\_buildings\_download\_region\_polygons.ipynb#scrollTo=0eXL156ae-iT](https://colab.research.google.com/github/google-research/google-research/blob/master/building_detection/open_buildings_download_region_polygons.ipynb#scrollTo=0eXL156ae-iT)

  * Google Research Colab notebook demonstrating how to download Open Buildings by region polygons via Earth Engine — great for prototyping.

* [https://colab.research.google.com/github/google-research/google-research/blob/master/building\_detection/open\_buildings\_spatial\_analysis\_examples.ipynb](https://colab.research.google.com/github/google-research/google-research/blob/master/building_detection/open_buildings_spatial_analysis_examples.ipynb)

  * Colab examples for spatial analysis on Open Buildings — helpful examples of filtering, aggregating, and visual checks.

* [https://colab.research.google.com/github/opengeos/leafmap/blob/master/docs/notebooks/81\_buildings.ipynb](https://colab.research.google.com/github/opengeos/leafmap/blob/master/docs/notebooks/81_buildings.ipynb)

  * leafmap notebook demonstrating visualization and interactions with building datasets using interactive maps in Colab.

* [https://colab.research.google.com/github/GFDRR/caribbean-rooftop-classification/blob/master/tutorials/01\_building\_delineation.ipynb#scrollTo=qk28lYyru2wC](https://colab.research.google.com/github/GFDRR/caribbean-rooftop-classification/blob/master/tutorials/01_building_delineation.ipynb#scrollTo=qk28lYyru2wC)

  * Tutorial focusing on rooftop/building delineation workflows — useful background on data cleaning and QA for footprints.

---

## Microsoft Building Footprints & Community Tools

* [https://github.com/microsoft/GlobalMLBuildingFootprints?tab=readme-ov-file](https://github.com/microsoft/GlobalMLBuildingFootprints?tab=readme-ov-file)

  * Microsoft’s GitHub repository for the Global Building Footprints releases. Contains download links, partitioning schemes, and release notes.

* [https://minedbuildings.z5.web.core.windows.net/global-buildings/buildings-with-height-coverage.geojson](https://minedbuildings.z5.web.core.windows.net/global-buildings/buildings-with-height-coverage.geojson)

  * A hosted GeoJSON sample of global building footprints including height coverage metadata — useful as a quick test file.

* [https://medium.com/vida-engineering/introducing-the-ultimate-cloud-native-building-footprints-dataset-17426b52dcec](https://medium.com/vida-engineering/introducing-the-ultimate-cloud-native-building-footprints-dataset-17426b52dcec)

  * Background article describing a cloud-native approach to working with building footprints and large vector datasets — useful design considerations.

---

## OpenStreetMap & Overpass / Conversion Tools

* [https://overpass-turbo.eu/](https://overpass-turbo.eu/)

  * Interactive Overpass query editor — excellent for building and testing Overpass QL queries manually before automating them.

* [https://github.com/tyrasd/osmtogeojson](https://github.com/tyrasd/osmtogeojson)

  * A lightweight tool to convert OSM JSON/XML to GeoJSON — useful when working with Overpass raw responses.

* [https://github.com/UrbanSystemsLab/Geofabrik-OSM-Extracts](https://github.com/UrbanSystemsLab/Geofabrik-OSM-Extracts)

  * Example tooling / repo around working with Geofabrik extracts (country/regional PBFs) — handy for bulk or offline workflows.

* [https://www.reddit.com/r/gis/comments/15gsm46/how\_to\_download\_google\_and\_microsoft\_building/](https://www.reddit.com/r/gis/comments/15gsm46/how_to_download_google_and_microsoft_building/)

  * Community discussion with practical tips and pointers for downloading building datasets (can surface informal but useful hacks).

* [https://samgeo.gishub.org/](https://samgeo.gishub.org/)

  * A GIS hub with resources and datasets (regional aggregation) — useful for regional data discovery and alternative extracts.

---

## Misc & Utilities

* [https://colab.research.google.com/github/opengeos/leafmap/blob/master/docs/notebooks/81\_buildings.ipynb](https://colab.research.google.com/github/opengeos/leafmap/blob/master/docs/notebooks/81_buildings.ipynb)

  * (Duplicated from above) leafmap tutorial for buildings visualization and small-scale processing.

---

## Suggested next actions for LINKS.md

* Add tags to each link (e.g., `tutorial`, `dataset`, `notebook`, `tool`) for easier filtering.
* Produce a `sources.json` manifest that pulls these links into a machine-readable catalog with fields like `name`, `url`, `type`, `license`, `notes`.
* I can also fetch summary metadata (license, typical file formats, last-updated) for each link and add it to this document.

---

*End of LINKS.md*
