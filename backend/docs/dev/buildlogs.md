===== Application Startup at 2025-09-18 09:31:45 =====

└─ platform: huggingface_spaces
├─ platform: huggingface_spaces
├─ config: loaded (api, gee, osm, web, export)
└─ config: loaded
INFO:     Started server process [1]
INFO:     Waiting for application startup.
[2025-09-18 09:32:15] atlas-gis-api v1.0.0 starting...
└─ static: mounted (/web/static)
DEBUG:google_auth_httplib2:Making request: POST https://oauth2.googleapis.com/token
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): oauth2.googleapis.com:443
DEBUG:urllib3.connectionpool:https://oauth2.googleapis.com:443 "POST /token HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): earthengine.googleapis.com:443
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "GET /$discovery/rest?version=v1&prettyPrint=false HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "GET /$discovery/rest?version=v1&prettyPrint=false HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "GET /v1/projects/grand-airport-464420-e3/algorithms?prettyPrint=false&alt=json HTTP/1.1" 200 None
*** Earth Engine *** Share your feedback by taking our Annual Developer Satisfaction Survey: https://google.qualtrics.com/jfe/form/SV_7TDKVSyKvBdmMqW?ref=4i2o6
└─ gee-auth: credentials ok
✓ Using individual environment variables for authentication
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "POST /v1/projects/grand-airport-464420-e3/value:compute?prettyPrint=false&alt=json HTTP/1.1" 200 None
└─ gee-conn: test passed
└─ sources: ready (7: microsoft, google, osm-buildings, osm-roads, osm-railways, osm-landmarks, osm-natural)
└─ server: ready on :7860

[startup completed in 1.2s]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
INFO:     10.16.0.181:6311 - "GET /web/ HTTP/1.1" 200 OK
INFO:     10.16.47.58:28993 - "GET /css/atlas.css?v=1 HTTP/1.1" 200 OK
INFO:     10.16.0.181:20367 - "GET /js/atlas.js?v=1 HTTP/1.1" 200 OK
INFO:     10.16.0.181:6311 - "GET /css/toast.css?v=1 HTTP/1.1" 200 OK
INFO:     10.16.14.52:30720 - "GET /js/toast.js?v=1 HTTP/1.1" 200 OK
INFO:src.api.routes.design_upload:===== NEW REQUEST: POST /api/v2/designs/upload at 2025-09-18 09:33:20 =====
INFO:src.api.routes.design_upload:Processing design upload: BSI Gatimu.kmz (application/vnd.google-earth.kmz)
INFO:src.api.routes.design_upload:Read 1406 bytes from BSI Gatimu.kmz
INFO:src.core.parsers.design_parser:Processing kmz file: BSI Gatimu.kmz
INFO:src.core.parsers.design_parser:Successfully parsed BSI Gatimu.kmz: 1 layers, 31 features in 0.00s
INFO:src.core.storage.design_storage:Stored design 8e12587b-e852-4df7-ac2a-36d098c6c842 with 1 layers
INFO:src.api.routes.design_upload:Design upload completed: 8e12587b-e852-4df7-ac2a-36d098c6c842 in 0.01s, 31 features
INFO:     10.16.41.192:25022 - "POST /api/v2/designs/upload HTTP/1.1" 200 OK
INFO:     10.16.16.100:57653 - "POST /api/v2/designs/render HTTP/1.1" 200 OK
INFO:src.api.routes.design_upload:===== NEW REQUEST: POST /api/v2/designs/render at 2025-09-18 09:33:20 =====
INFO:src.api.routes.design_upload:Rendering design 8e12587b-e852-4df7-ac2a-36d098c6c842
INFO:src.api.routes.design_upload:Design rendering completed: 8e12587b-e852-4df7-ac2a-36d098c6c842 in 0.00s, 31 features
INFO:src.api.routes.extract_v2:===== NEW REQUEST: POST /api/v2/extract at 2025-09-18 09:36:48 =====
INFO:src.api.routes.extract_v2:Starting raw data extraction job 876e6005-d5ad-46b7-b524-da33c403ec84
INFO:src.core.services.processing_service:Processing extraction for 4 data sources
INFO:src.core.services.processing_service:AOI validated: 0.10 km²
DEBUG:urllib3.connectionpool:Resetting dropped connection: oauth2.googleapis.com
DEBUG:urllib3.connectionpool:https://oauth2.googleapis.com:443 "POST /token HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:Resetting dropped connection: earthengine.googleapis.com
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "GET /$discovery/rest?version=v1&prettyPrint=false HTTP/1.1" 200 None
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "GET /$discovery/rest?version=v1&prettyPrint=false HTTP/1.1" 200 None
INFO:src.core.data_sources.google_earth_engine.google_buildings:Google Earth Engine initialized successfully
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "POST /v1/projects/grand-airport-464420-e3/value:compute?prettyPrint=false&alt=json HTTP/1.1" 200 None
INFO:src.core.data_sources.google_earth_engine.google_buildings:Found 272 Google Open Buildings in AOI
INFO:src.core.data_sources.google_earth_engine.google_buildings:Extracting ALL 272 Google Open Buildings - no limits applied
DEBUG:urllib3.connectionpool:https://earthengine.googleapis.com:443 "POST /v1/projects/grand-airport-464420-e3/value:compute?prettyPrint=false&alt=json HTTP/1.1" 200 None
INFO:src.core.data_sources.google_earth_engine.google_buildings:Successfully extracted and processed 272 Google Open Buildings with clean properties
INFO:src.core.services.processing_service:Source google_buildings completed: 272 features in 7.40s
INFO:src.core.data_sources.openstreetmap.osm_natural:Converting 0 raw OSM elements to GeoJSON
INFO:src.core.data_sources.openstreetmap.osm_natural:Successfully converted 0 OSM natural features
INFO:src.core.services.processing_service:Source osm_natural completed: 0 features in 0.57s
INFO:src.core.data_sources.openstreetmap.osm_roads:Converting 39 raw OSM elements to GeoJSON
INFO:src.core.data_sources.openstreetmap.osm_roads:Successfully converted 39 OSM roads features
INFO:src.core.services.processing_service:Source osm_roads completed: 39 features in 0.58s
INFO:src.core.data_sources.openstreetmap.osm_landmarks:Converting 0 raw OSM elements to GeoJSON
INFO:src.core.data_sources.openstreetmap.osm_landmarks:Successfully converted 0 OSM landmarks features
INFO:src.core.services.processing_service:Source osm_landmarks completed: 0 features in 0.69s
INFO:src.core.services.processing_service:Completed processing: 4 sources processed
INFO:src.api.routes.extract_v2:Geometry cleaning enabled with config: {'min_area_m2': 12, 'simplify_tolerance_m': 0.001, 'google_min_confidence': 0.7, 'min_width_m': 3, 'min_compactness': 0.12, 'max_elongation': 6, 'strategy': 'highest_confidence', 'make_valid': True}
INFO:src.api.routes.extract_v2:Using unified BuildingsCleaner (source-specific)
INFO:src.core.processors.buildings_cleaner:Cleaning google_buildings: 272 features
INFO:src.core.processors.buildings_cleaner:google_buildings: removed 24 features below confidence 0.7
INFO:src.core.processors.buildings_cleaner:google_buildings: removed 36 < 12m²
INFO:src.core.processors.buildings_cleaner:google_buildings: removed 25 by shape filters (width≥3m, compactness≥0.12, elongation≤6)
INFO:src.api.routes.extract_v2:Unified cleaning for google_buildings: 272 → 187
INFO:src.api.routes.extract_v2:Roads clipping enabled (clean_roads=True)
INFO:src.core.processors.roads_cleaner:osm_roads: clipped 39 → 20 to AOI
INFO:src.api.routes.extract_v2:Roads clipped for osm_roads: 39 → 20
INFO:src.api.routes.extract_v2:Job 876e6005-d5ad-46b7-b524-da33c403ec84 completed in 8.37s: 207 features from 4/4 sources
INFO:     10.16.0.181:50580 - "POST /api/v2/extract HTTP/1.1" 200 OK
INFO:src.api.routes.download_v2:===== NEW REQUEST: GET /api/v2/download/876e6005-d5ad-46b7-b524-da33c403ec84/kmz at 2025-09-18 09:37:55 =====
INFO:src.api.routes.download_v2:Download request: job=876e6005-d5ad-46b7-b524-da33c403ec84, format=kmz
INFO:     10.16.0.181:34762 - "GET /api/v2/download/876e6005-d5ad-46b7-b524-da33c403ec84/kmz HTTP/1.1" 404 Not Found
INFO:src.api.routes.download_v2:===== NEW REQUEST: POST /api/v2/download-inline/kmz at 2025-09-18 09:37:56 =====
INFO:     10.16.41.192:37658 - "POST /api/v2/download-inline/kmz HTTP/1.1" 200 OK
INFO:     10.16.14.52:55754 - "GET / HTTP/1.1" 307 Temporary Redirect
INFO:     10.16.14.52:55754 - "GET /web/ HTTP/1.1" 200 OK