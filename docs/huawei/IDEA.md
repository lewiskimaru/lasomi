\# DQODN 3.0 Automated Fiber Design System

\## System Architecture \& Implementation Plan



---



\## 1. Executive Summary



\### Problem Statement

Manual DQODN 3.0 fiber network design is time-consuming despite having well-defined rules. Designers spend hours clustering SDUs, routing cables along poles, calculating splits, and generating BoQs—tasks that are highly automatable given deterministic GIS data.



\### Solution

A web-based recommendation engine that ingests field survey data (poles, buildings, infrastructure) and generates multiple design scenarios with cost tradeoffs. The system augments human designers rather than replacing them, allowing rapid iteration and informed decision-making.



\### Success Criteria

\- ✅ Reduce design time from days to hours

\- ✅ Generate 2-5 viable scenarios per project

\- ✅ 90%+ accuracy in cable length calculations

\- ✅ Designer adoption rate >70% within 6 months



---



\## 2. Core Objectives



\### What We're Building

1\. \*\*Data Ingestion Pipeline\*\* - Parse KMZ/CSV field survey data

2\. \*\*Visualization Interface\*\* - Interactive map for viewing/editing designs

3\. \*\*Design Generation Engine\*\* - Algorithmic clustering and routing

4\. \*\*Scenario Comparison\*\* - Cost/performance tradeoffs

5\. \*\*Export System\*\* - BoQ, material schedules, design KMZ



\### What We're NOT Building (Yet)

\- ❌ User authentication/accounts

\- ❌ Long-term data storage (>7 days)

\- ❌ Real-time collaboration

\- ❌ Mobile app

\- ❌ Integration with NCE or other Huawei systems



---



\## 3. System Architecture



```

┌─────────────────────────────────────────────────────────────┐

│                     FRONTEND (React)                        │

├─────────────────────────────────────────────────────────────┤

│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │

│  │ Map Interface│  │ Data Editor  │  │ Scenario     │     │

│  │ (Mapbox/     │  │ (Forms +     │  │ Comparison   │     │

│  │  Leaflet)    │  │  Tables)     │  │ (Cards/Grid) │     │

│  └──────────────┘  └──────────────┘  └──────────────┘     │

│                                                             │

│  State Management: IndexedDB (job persistence)              │

└─────────────────────────────────────────────────────────────┘

&nbsp;                           ▲ REST API (JSON)

&nbsp;                           │

┌─────────────────────────────────────────────────────────────┐

│                    BACKEND (FastAPI)                        │

├─────────────────────────────────────────────────────────────┤

│                                                             │

│  ┌───────────────────────────────────────────────────────┐ │

│  │          API LAYER (FastAPI Routes)                   │ │

│  ├───────────────────────────────────────────────────────┤ │

│  │ • POST /jobs/create      → Create new design job      │ │

│  │ • POST /jobs/{id}/upload → Upload HLD data (KMZ/CSV)  │ │

│  │ • GET  /jobs/{id}/data   → Retrieve parsed GeoJSON    │ │

│  │ • POST /jobs/{id}/design → Generate scenarios         │ │

│  │ • GET  /jobs/{id}/boq    → Export BoQ (Excel/CSV)     │ │

│  │ • GET  /jobs/{id}/export → Export KMZ design          │ │

│  └───────────────────────────────────────────────────────┘ │

│                                                             │

│  ┌───────────────────────────────────────────────────────┐ │

│  │          CORE MODULES                                 │ │

│  ├───────────────────────────────────────────────────────┤ │

│  │                                                       │ │

│  │  1. DATA PROCESSING MODULE                            │ │

│  │     - KMZ Parser (fiona, geopandas)                   │ │

│  │     - CSV Parser (pandas)                             │ │

│  │     - GeoJSON Validator                               │ │

│  │     - Coordinate System Handler (pyproj)              │ │

│  │                                                       │ │

│  │  2. DESIGN ENGINE MODULE                              │ │

│  │     - SDU Clustering Algorithm                        │ │

│  │     - HubBox Placement Optimizer                      │ │

│  │     - SubBox Cascade Generator                        │ │

│  │     - Cable Routing Engine (NetworkX)                 │ │

│  │     - Split Ratio Calculator                          │ │

│  │     - Loss Budget Validator                           │ │

│  │                                                       │ │

│  │  3. SCENARIO GENERATOR MODULE                         │ │

│  │     - Multi-objective Optimizer                       │ │

│  │     - Cost Calculator                                 │ │

│  │     - Performance Scorer                              │ │

│  │     - Scenario Ranker                                 │ │

│  │                                                       │ │

│  │  4. EXPORT MODULE                                     │ │

│  │     - BoQ Generator (openpyxl)                        │ │

│  │     - Material Schedule                               │ │

│  │     - KMZ Exporter (simplekml)                        │ │

│  │     - Design Report (PDF)                             │ │

│  │                                                       │ │

│  └───────────────────────────────────────────────────────┘ │

│                                                             │

│  ┌───────────────────────────────────────────────────────┐ │

│  │          JOB MANAGER (Stateless)                      │ │

│  ├───────────────────────────────────────────────────────┤ │

│  │ • UUID-based job IDs                                  │ │

│  │ • File-based storage (/tmp/jobs/{job\_id}/)            │ │

│  │ • TTL: 7 days (background cleanup task)               │ │

│  │ • Structure:                                          │ │

│  │   /tmp/jobs/                                          │ │

│  │   └── {job\_id}/                                       │ │

│  │       ├── metadata.json (created\_at, expires\_at)      │ │

│  │       ├── inputs/                                     │ │

│  │       │   ├── poles.geojson                           │ │

│  │       │   ├── buildings.geojson                       │ │

│  │       │   └── infrastructure.geojson                  │ │

│  │       ├── outputs/                                    │ │

│  │       │   ├── scenario\_1.geojson                      │ │

│  │       │   ├── scenario\_2.geojson                      │ │

│  │       │   └── boq.xlsx                                │ │

│  │       └── logs/                                       │ │

│  │           └── design.log                              │ │

│  └───────────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────────┘

&nbsp;                           │

&nbsp;                           ▼

┌─────────────────────────────────────────────────────────────┐

│            EPHEMERAL STORAGE (HuggingFace Spaces)           │

│  • 7-day retention                                          │

│  • Background cron job: cleanup expired jobs                │

└─────────────────────────────────────────────────────────────┘

```



---



\## 4. Data Model



\### Input Data Types



\#### 4.1 Poles

```json

{

&nbsp; "type": "FeatureCollection",

&nbsp; "features": \[

&nbsp;   {

&nbsp;     "type": "Feature",

&nbsp;     "geometry": {

&nbsp;       "type": "Point",

&nbsp;       "coordinates": \[lon, lat]

&nbsp;     },

&nbsp;     "properties": {

&nbsp;       "id": "POLE\_001",

&nbsp;       "type": "existing|new|third\_party",

&nbsp;       "height": 7.0,  // meters

&nbsp;       "owner": "operator\_name",

&nbsp;       "capacity": "available|full",

&nbsp;       "notes": "string"

&nbsp;     }

&nbsp;   }

&nbsp; ]

}

```



\#### 4.2 Buildings (SDU/MDU/UC)

```json

{

&nbsp; "type": "FeatureCollection",

&nbsp; "features": \[

&nbsp;   {

&nbsp;     "type": "Feature",

&nbsp;     "geometry": {

&nbsp;       "type": "Point|Polygon",

&nbsp;       "coordinates": \[...]

&nbsp;     },

&nbsp;     "properties": {

&nbsp;       "id": "BLD\_001",

&nbsp;       "type": "SDU|MDU|UC",

&nbsp;       "units": 1,  // For MDU: number of units

&nbsp;       "address": "string",

&nbsp;       "status": "active|planned",

&nbsp;       "priority": "high|medium|low"

&nbsp;     }

&nbsp;   }

&nbsp; ]

}

```



\#### 4.3 Infrastructure (XBox, OLT, etc.)

```json

{

&nbsp; "type": "FeatureCollection",

&nbsp; "features": \[

&nbsp;   {

&nbsp;     "type": "Feature",

&nbsp;     "geometry": {

&nbsp;       "type": "Point",

&nbsp;       "coordinates": \[lon, lat]

&nbsp;     },

&nbsp;     "properties": {

&nbsp;       "id": "XBOX\_001",

&nbsp;       "type": "xbox|olt|odf|existing\_fiber",

&nbsp;       "capacity": {

&nbsp;         "total\_ports": 12,

&nbsp;         "available\_ports": 8

&nbsp;       },

&nbsp;       "status": "active"

&nbsp;     }

&nbsp;   }

&nbsp; ]

}

```



\#### 4.4 Road Networks (From AtlaSOmi/OSM)

```json

{

&nbsp; "type": "FeatureCollection",

&nbsp; "features": \[

&nbsp;   {

&nbsp;     "type": "Feature",

&nbsp;     "geometry": {

&nbsp;       "type": "LineString",

&nbsp;       "coordinates": \[\[lon, lat], ...]

&nbsp;     },

&nbsp;     "properties": {

&nbsp;       "id": "ROAD\_001",

&nbsp;       "name": "Main Street",

&nbsp;       "type": "primary|secondary|residential",

&nbsp;       "surface": "paved|unpaved"

&nbsp;     }

&nbsp;   }

&nbsp; ]

}

```



\### Output Data Types



\#### 4.5 Design Scenario

```json

{

&nbsp; "scenario\_id": "uuid",

&nbsp; "job\_id": "uuid",

&nbsp; "created\_at": "iso\_timestamp",

&nbsp; "metadata": {

&nbsp;   "scenario\_name": "Scenario A - Minimal Cost",

&nbsp;   "total\_cost": 45000.00,

&nbsp;   "total\_homes\_passed": 128,

&nbsp;   "avg\_loss\_budget": 22.5,  // dB

&nbsp;   "cable\_utilization": 0.85

&nbsp; },

&nbsp; "components": {

&nbsp;   "hubboxes": \[...],

&nbsp;   "subboxes": \[...],

&nbsp;   "endboxes": \[...],

&nbsp;   "cables": \[...]

&nbsp; },

&nbsp; "geometry": {

&nbsp;   // GeoJSON FeatureCollection

&nbsp; }

}

```



---



\## 5. Core Algorithms



\### 5.1 SDU Clustering Algorithm



\*\*Objective:\*\* Group SDUs into clusters of ≤32 homes (1:32) or ≤64 homes (1:64)



\*\*Approach:\*\* Modified K-means with constraints



```python

def cluster\_sdus(buildings, max\_cluster\_size=32):

&nbsp;   """

&nbsp;   Constraint-based clustering algorithm

&nbsp;   

&nbsp;   Constraints:

&nbsp;   - Max homes per cluster ≤ max\_cluster\_size

&nbsp;   - Respect road network (no straight-line clustering)

&nbsp;   - Prioritize geographic proximity

&nbsp;   - Handle MDUs separately (dedicated chains)

&nbsp;   - Consider UCs in future planning

&nbsp;   """

&nbsp;   

&nbsp;   # Step 1: Separate SDUs, MDUs, UCs

&nbsp;   sdus = \[b for b in buildings if b.type == 'SDU']

&nbsp;   mdus = \[b for b in buildings if b.type == 'MDU']

&nbsp;   

&nbsp;   # Step 2: For each MDU, create dedicated cluster

&nbsp;   mdu\_clusters = \[create\_mdu\_cluster(mdu) for mdu in mdus]

&nbsp;   

&nbsp;   # Step 3: Cluster SDUs using constrained k-means

&nbsp;   # - Build road network graph

&nbsp;   # - Calculate shortest path distances (not euclidean)

&nbsp;   # - Apply k-means with max\_size constraint

&nbsp;   # - Iteratively split oversized clusters

&nbsp;   

&nbsp;   # Step 4: Validate split ratios (1:64 or 1:32)

&nbsp;   

&nbsp;   return clusters

```



\*\*Heuristic Improvements:\*\*

\- \*\*Seed selection:\*\* Start with geographically extreme points

\- \*\*Road snapping:\*\* Snap building centroids to nearest road node

\- \*\*Hierarchical clustering:\*\* Large areas → subdivide recursively



\### 5.2 HubBox Placement



\*\*Objective:\*\* Find optimal HubBox location for each cluster



\*\*Approach:\*\* Weighted centroid with accessibility constraints



```python

def place\_hubbox(cluster, poles, roads):

&nbsp;   """

&nbsp;   Place HubBox at accessible location minimizing cable length

&nbsp;   

&nbsp;   Steps:

&nbsp;   1. Calculate geographic centroid of cluster

&nbsp;   2. Find nearest pole with capacity

&nbsp;   3. Validate accessibility (road access, ROW)

&nbsp;   4. Calculate total cable length to all SubBoxes

&nbsp;   5. If suboptimal, iterate to adjacent poles

&nbsp;   """

&nbsp;   

&nbsp;   centroid = calculate\_weighted\_centroid(cluster.buildings)

&nbsp;   candidate\_poles = find\_nearby\_poles(centroid, poles, radius=500)

&nbsp;   

&nbsp;   best\_pole = None

&nbsp;   min\_total\_cable = float('inf')

&nbsp;   

&nbsp;   for pole in candidate\_poles:

&nbsp;       total\_cable = estimate\_cable\_length(pole, cluster)

&nbsp;       if total\_cable < min\_total\_cable:

&nbsp;           best\_pole = pole

&nbsp;           min\_total\_cable = total\_cable

&nbsp;   

&nbsp;   return best\_pole

```



\### 5.3 SubBox Cascade Routing



\*\*Objective:\*\* Create daisy-chain of 4 SubBoxes + 1 EndBox



\*\*Approach:\*\* Traveling Salesman Problem (TSP) variant with road constraints



```python

def route\_subbox\_cascade(hubbox, cluster\_buildings, poles, roads):

&nbsp;   """

&nbsp;   Create optimal cascade path for SubBoxes

&nbsp;   

&nbsp;   DQODN Rules:

&nbsp;   - Max 4 SubBoxes per chain

&nbsp;   - 1:9 uneven splitter (70% cascade, 30% drop)

&nbsp;   - EndBox at terminal position (1:8 even)

&nbsp;   - Follow road network

&nbsp;   """

&nbsp;   

&nbsp;   # Step 1: Divide cluster into 4 sub-groups (8 homes each)

&nbsp;   sub\_groups = divide\_cluster(cluster\_buildings, n=4)

&nbsp;   

&nbsp;   # Step 2: Place SubBox for each sub-group

&nbsp;   subboxes = \[]

&nbsp;   for group in sub\_groups:

&nbsp;       pole = find\_nearest\_pole\_with\_capacity(group, poles)

&nbsp;       subboxes.append(SubBox(pole, group))

&nbsp;   

&nbsp;   # Step 3: Optimize cascade order (minimize cable length)

&nbsp;   # Use nearest-neighbor heuristic (greedy TSP)

&nbsp;   ordered\_subboxes = order\_cascade(hubbox, subboxes, roads)

&nbsp;   

&nbsp;   # Step 4: Add EndBox at end of chain

&nbsp;   endbox = place\_endbox(ordered\_subboxes\[-1], cluster\_buildings)

&nbsp;   

&nbsp;   # Step 5: Route cables along roads (Dijkstra shortest path)

&nbsp;   cable\_routes = \[]

&nbsp;   prev = hubbox

&nbsp;   for box in ordered\_subboxes + \[endbox]:

&nbsp;       route = route\_cable\_along\_roads(prev, box, roads)

&nbsp;       cable\_routes.append(route)

&nbsp;       prev = box

&nbsp;   

&nbsp;   return ordered\_subboxes, endbox, cable\_routes

```



\### 5.4 Cable Length Calculation



\*\*Critical for DQODN:\*\* Pre-terminated cables come in fixed lengths



```python

STANDARD\_CABLE\_LENGTHS = \[50, 100, 150, 200, 250, 300, 400, 500]  # meters



def calculate\_cable\_requirements(route):

&nbsp;   """

&nbsp;   Map actual distance to nearest standard cable length

&nbsp;   Add slack (typically 10%)

&nbsp;   """

&nbsp;   actual\_distance = sum(\[

&nbsp;       haversine(route\[i], route\[i+1]) 

&nbsp;       for i in range(len(route)-1)

&nbsp;   ])

&nbsp;   

&nbsp;   slack\_factor = 1.10  # 10% slack for loops, pole mounting

&nbsp;   required\_length = actual\_distance \* slack\_factor

&nbsp;   

&nbsp;   # Select next larger standard length

&nbsp;   cable\_length = min(\[

&nbsp;       l for l in STANDARD\_CABLE\_LENGTHS 

&nbsp;       if l >= required\_length

&nbsp;   ])

&nbsp;   

&nbsp;   return cable\_length, actual\_distance

```



\### 5.5 Accessory Assignment



\*\*Objective:\*\* Auto-assign tension clamps, tangents, J-hooks based on pole positions



```python

def assign\_accessories(cable\_route, poles):

&nbsp;   """

&nbsp;   Rules:

&nbsp;   - Tension clamp: Direction change >30°, span >100m

&nbsp;   - Tangent: Direction change 15-30°

&nbsp;   - J-hook: Straight runs, every 50m

&nbsp;   - Slack storage bracket: At every box

&nbsp;   """

&nbsp;   

&nbsp;   accessories = \[]

&nbsp;   

&nbsp;   for i in range(1, len(cable\_route)-1):

&nbsp;       prev, curr, next = cable\_route\[i-1:i+2]

&nbsp;       

&nbsp;       angle = calculate\_angle(prev, curr, next)

&nbsp;       span\_length = haversine(prev, curr)

&nbsp;       

&nbsp;       if angle > 30 or span\_length > 100:

&nbsp;           accessories.append(TensionClamp(curr))

&nbsp;       elif angle > 15:

&nbsp;           accessories.append(Tangent(curr))

&nbsp;       else:

&nbsp;           # Place J-hooks every 50m on straight runs

&nbsp;           num\_jhooks = int(span\_length / 50)

&nbsp;           accessories.extend(\[JHook(curr) for \_ in range(num\_jhooks)])

&nbsp;   

&nbsp;   return accessories

```



---



\## 6. Scenario Generation



\*\*Generate 3-5 scenarios with different optimization objectives:\*\*



\### Scenario Types



1\. \*\*Minimal Cost\*\*

&nbsp;  - Minimize total cable length

&nbsp;  - Use maximum split ratio (1:64)

&nbsp;  - Prefer existing poles over new poles



2\. \*\*Minimal Loss Budget\*\*

&nbsp;  - Minimize optical path length

&nbsp;  - Use conservative split ratios (1:32)

&nbsp;  - Shorter cable runs (more direct routing)



3\. \*\*Fastest Deployment\*\*

&nbsp;  - Minimize number of new poles

&nbsp;  - Maximize use of existing infrastructure

&nbsp;  - Simplify cascade topology



4\. \*\*Balanced\*\* (Default)

&nbsp;  - Weight cost, loss, and deployment time equally



5\. \*\*Custom\*\* (Future)

&nbsp;  - User-defined weights for objectives



\### Scoring Function



```python

def score\_scenario(scenario, weights):

&nbsp;   """

&nbsp;   Multi-objective scoring

&nbsp;   """

&nbsp;   cost\_score = calculate\_cost(scenario)

&nbsp;   loss\_score = calculate\_max\_loss(scenario)

&nbsp;   complexity\_score = calculate\_topology\_complexity(scenario)

&nbsp;   

&nbsp;   total\_score = (

&nbsp;       weights\['cost'] \* normalize(cost\_score) +

&nbsp;       weights\['loss'] \* normalize(loss\_score) +

&nbsp;       weights\['complexity'] \* normalize(complexity\_score)

&nbsp;   )

&nbsp;   

&nbsp;   return total\_score

```



---



\## 7. Technology Stack



\### Backend (Python)



```yaml

Core Framework:

&nbsp; - FastAPI (async web framework)

&nbsp; - Uvicorn (ASGI server)

&nbsp; - Pydantic (data validation)



GIS Processing:

&nbsp; - geopandas (GeoDataFrame operations)

&nbsp; - shapely (geometric operations)

&nbsp; - fiona (KMZ/Shapefile reading)

&nbsp; - pyproj (coordinate transformations)

&nbsp; - GDAL (via fiona, for format support)



Graph Algorithms:

&nbsp; - networkx (road network routing, TSP)

&nbsp; - scipy (spatial algorithms, clustering)

&nbsp; - scikit-learn (k-means clustering)



Export/Import:

&nbsp; - simplekml (KMZ export)

&nbsp; - openpyxl (Excel BoQ export)

&nbsp; - pandas (CSV handling)



Utilities:

&nbsp; - uuid (job ID generation)

&nbsp; - apscheduler (background cleanup tasks)

&nbsp; - python-multipart (file uploads)

```



\### Frontend (React)



```yaml

Core:

&nbsp; - React 18

&nbsp; - TypeScript

&nbsp; - Vite (build tool)



Mapping:

&nbsp; - Mapbox GL JS (or Leaflet for open-source)

&nbsp; - deck.gl (advanced visualizations)

&nbsp; - turf.js (client-side GIS operations)



State Management:

&nbsp; - React Context (global state)

&nbsp; - IndexedDB (localForage wrapper)



UI Components:

&nbsp; - TailwindCSS (styling)

&nbsp; - shadcn/ui (component library)

&nbsp; - react-hook-form (forms)



File Handling:

&nbsp; - jszip (KMZ creation/extraction)

&nbsp; - papaparse (CSV parsing)

```



\### Deployment (MVP)



```yaml

Platform: HuggingFace Spaces (Free tier)

&nbsp; - Gradio/Streamlit alternative: Custom FastAPI + React

&nbsp; - Storage: Ephemeral filesystem (/tmp)

&nbsp; - TTL: 7 days (automated cleanup)



CI/CD: GitHub Actions

&nbsp; - Automated testing

&nbsp; - Docker build

&nbsp; - Deploy to HF Spaces on push to main

```



---



\## 8. API Design



\### REST Endpoints



```yaml

POST /api/v1/jobs

&nbsp; Description: Create new design job

&nbsp; Request: {}

&nbsp; Response: { job\_id: uuid, expires\_at: timestamp }



POST /api/v1/jobs/{job\_id}/upload

&nbsp; Description: Upload HLD data files

&nbsp; Request: FormData (KMZ/CSV files)

&nbsp; Response: { parsed: true, features\_count: {...} }



GET /api/v1/jobs/{job\_id}/data

&nbsp; Description: Retrieve parsed GeoJSON

&nbsp; Response: { poles: GeoJSON, buildings: GeoJSON, ... }



POST /api/v1/jobs/{job\_id}/generate

&nbsp; Description: Generate design scenarios

&nbsp; Request: { 

&nbsp;   split\_ratio: "1:32|1:64",

&nbsp;   scenario\_count: 3,

&nbsp;   optimize\_for: "cost|loss|balanced"

&nbsp; }

&nbsp; Response: { 

&nbsp;   scenarios: \[

&nbsp;     { scenario\_id, name, cost, loss, geometry },

&nbsp;     ...

&nbsp;   ]

&nbsp; }



GET /api/v1/jobs/{job\_id}/scenarios/{scenario\_id}

&nbsp; Description: Get detailed scenario data

&nbsp; Response: { full\_scenario\_object }



GET /api/v1/jobs/{job\_id}/export/boq

&nbsp; Description: Export Bill of Quantities

&nbsp; Query: ?scenario\_id=uuid\&format=xlsx|csv

&nbsp; Response: File download



GET /api/v1/jobs/{job\_id}/export/kmz

&nbsp; Description: Export design as KMZ

&nbsp; Query: ?scenario\_id=uuid

&nbsp; Response: KMZ file download



DELETE /api/v1/jobs/{job\_id}

&nbsp; Description: Manually delete job

&nbsp; Response: { deleted: true }

```



---



\## 9. File Management (No Database)



\### Job Storage Structure



```

/tmp/jobs/

├── {job\_id\_1}/

│   ├── metadata.json          # { created\_at, expires\_at, status }

│   ├── inputs/

│   │   ├── poles.geojson

│   │   ├── buildings.geojson

│   │   ├── infrastructure.geojson

│   │   └── roads.geojson

│   ├── outputs/

│   │   ├── scenario\_minimal\_cost.geojson

│   │   ├── scenario\_minimal\_loss.geojson

│   │   ├── scenario\_balanced.geojson

│   │   └── boq\_minimal\_cost.xlsx

│   └── logs/

│       └── processing.log

├── {job\_id\_2}/

│   └── ...

└── cleanup.lock               # Prevent concurrent cleanup

```



\### Cleanup Strategy



```python

\# Background task (APScheduler)

@scheduler.scheduled\_job('cron', hour=2)  # Run at 2 AM daily

def cleanup\_expired\_jobs():

&nbsp;   jobs\_dir = Path("/tmp/jobs")

&nbsp;   now = datetime.utcnow()

&nbsp;   

&nbsp;   for job\_dir in jobs\_dir.iterdir():

&nbsp;       metadata\_file = job\_dir / "metadata.json"

&nbsp;       if metadata\_file.exists():

&nbsp;           metadata = json.loads(metadata\_file.read\_text())

&nbsp;           expires\_at = datetime.fromisoformat(metadata\['expires\_at'])

&nbsp;           

&nbsp;           if now > expires\_at:

&nbsp;               shutil.rmtree(job\_dir)

&nbsp;               logger.info(f"Deleted expired job: {job\_dir.name}")

```



\### Concurrency Handling



```python

import fcntl  # File locking



def get\_job\_with\_lock(job\_id):

&nbsp;   """Acquire file lock before reading/writing job data"""

&nbsp;   lock\_file = Path(f"/tmp/jobs/{job\_id}/.lock")

&nbsp;   lock\_file.touch()

&nbsp;   

&nbsp;   with open(lock\_file, 'r') as f:

&nbsp;       fcntl.flock(f.fileno(), fcntl.LOCK\_EX)  # Exclusive lock

&nbsp;       # Perform operations

&nbsp;       yield job\_id

&nbsp;       fcntl.flock(f.fileno(), fcntl.LOCK\_UN)  # Release lock

```



---



\## 10. Frontend Architecture



\### Component Hierarchy



```

App

├── JobManager (IndexedDB interface)

│   ├── CreateJob

│   ├── JobList (local jobs)

│   └── JobDetails

│

├── MapInterface

│   ├── BaseMap (Mapbox/Leaflet)

│   ├── LayerControls

│   │   ├── PolesLayer

│   │   ├── BuildingsLayer

│   │   ├── InfrastructureLayer

│   │   └── RoadsLayer

│   ├── DrawingTools (draw polygons for manual clustering)

│   └── ScenarioVisualization

│       ├── HubBoxMarkers

│       ├── SubBoxMarkers

│       ├── CableRoutes

│       └── AccessoryIcons

│

├── DataEditor

│   ├── FileUploader (KMZ/CSV)

│   ├── FeatureTable (edit poles, buildings)

│   └── ValidationPanel

│

├── ScenarioPanel

│   ├── GenerateButton

│   ├── ScenarioCards

│   │   ├── CostMetrics

│   │   ├── LossMetrics

│   │   └── DeploymentMetrics

│   └── ComparisonTable

│

└── ExportPanel

&nbsp;   ├── BoQDownload

&nbsp;   ├── KMZDownload

&nbsp;   └── ReportDownload

```



\### State Management Pattern



```typescript

// Context API for global state

interface AppState {

&nbsp; currentJobId: string | null;

&nbsp; jobData: {

&nbsp;   poles: GeoJSON.FeatureCollection;

&nbsp;   buildings: GeoJSON.FeatureCollection;

&nbsp;   infrastructure: GeoJSON.FeatureCollection;

&nbsp;   roads: GeoJSON.FeatureCollection;

&nbsp; };

&nbsp; scenarios: Scenario\[];

&nbsp; selectedScenario: string | null;

}



// IndexedDB schema

const db = await openDB('dqodn-designer', 1, {

&nbsp; upgrade(db) {

&nbsp;   db.createObjectStore('jobs', { keyPath: 'job\_id' });

&nbsp;   db.createObjectStore('scenarios', { keyPath: 'scenario\_id' });

&nbsp; }

});



// Persist job data locally

await db.put('jobs', {

&nbsp; job\_id: uuid,

&nbsp; created\_at: new Date(),

&nbsp; expires\_at: new Date(Date.now() + 7 \* 24 \* 60 \* 60 \* 1000),

&nbsp; data: jobData

});

```



---



