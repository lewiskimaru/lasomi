# Fiber Network Planning & Design Automation Project

## Document Purpose
This document serves as a comprehensive reference for automation initiatives within the fiber network planning and design workflow. It captures current manual processes, automation solutions already implemented, and planned future automation to increase efficiency and reduce repetitive tasks.

**Last Updated:** September 29, 2025  
**Author:** Network Planning & Design Graduate Trainee  
**Project Duration:** Started Month 1 of role

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current Manual Workflow](#current-manual-workflow)
3. [Phase 1: Building & Road Extraction (COMPLETED)](#phase-1-building--road-extraction-completed)
4. [Phase 2: Pole Accessorizing Automation (PLANNED)](#phase-2-pole-accessorizing-automation-planned)
5. [Phase 3: Measurement & Cable Scheduling (PLANNED)](#phase-3-measurement--cable-scheduling-planned)
6. [Phase 4: FTTH Design Recommendation Engine (PLANNED)](#phase-4-ftth-design-recommendation-engine-planned)
7. [Technical Architecture](#technical-architecture)
8. [Impact Metrics](#impact-metrics)
9. [Challenges & Considerations](#challenges--considerations)

---

## Executive Summary

The fiber network planning and design process involves significant manual, repetitive tasks that are rules-based and data-driven, making them ideal candidates for automation. This project aims to progressively automate the design workflow while maintaining design quality and allowing human designers to focus on strategic decision-making rather than mechanical execution.

**Key Achievements:**
- Automated building footprint and road extraction (saving ~X hours per design)
- Reduced manual tracing work by ~XX%

**Planned Automation:**
- Pole accessorizing based on network topology rules
- Automated measurement and cable scheduling
- FTTH design recommendation engine for generating design alternatives

---

## Current Manual Workflow

### Overview
The fiber network planning and design process follows this general sequence:

```
Data Collection → Google Earth Pro Tracing → AutoCAD Design → Accessorizing → 
Measurement → Documentation → Output (HLD/LLD PDFs)
```

### Detailed Process Steps

#### 1. Data Collection (Field Survey)
**What happens:**
- Field teams collect geographic data about the deployment area
- Data collected includes:
  - House/building locations and clustering
  - Pole positions for aerial deployment
  - Manholes and underground infrastructure
  - Existing infrastructure (cables, equipment)
  - Proposed infrastructure locations

**Output:** Raw survey data (coordinates, descriptions, counts)

**Current state:** Manual field work (cannot be automated)

---

#### 2. Google Earth Pro Tracing
**What happens:**
- Import survey data into Google Earth Pro
- Manually trace roads following actual paths
- Manually trace building footprints
- Mark landmarks and reference points
- Create KMZ files with traced features

**Pain points:**
- Extremely time-consuming (hours per design area)
- Prone to human error and inconsistency
- Low-value work that doesn't require design expertise
- Repetitive clicking and drawing

**Status:** ✅ **AUTOMATED** (See Phase 1)

---

#### 3. AutoCAD Design Transfer
**What happens:**
- Transfer traced data from Google Earth Pro to AutoCAD
- Create detailed Low-Level Design (LLD) drawings
- Place network elements (poles, cabinets, FDTs, cables)
- Define cable paths and routing
- Determine hardware specifications

**Output:** AutoCAD drawings with network topology

**Current state:** Semi-manual (data transfer automated, design placement manual)

---

#### 4. Network Accessorizing
**What happens:**
- For each pole in the network, define required accessories based on:
  - Pole position in network (corner, straight, junction)
  - Relationship to adjacent poles (bearing changes, span distances)
  - Environmental factors (road crossings, third-party poles, electrical equipment)
  - Network type (FTTB vs FTTH)
  - Physical constraints (distances, angles, cable slack requirements)

**Typical accessories:**
- **Tension clamps:** 2x at corners (bearing change > threshold)
- **Slack storage:** 20m at road crossings + storage hardware + downlead + UPB
- **Tangents:** For FTTB, placed every 2-3 poles or based on span distance
- **J-hooks:** For FTTH, placed every 2-3 poles or based on span distance
- **Special markers:** For third-party poles or electrical equipment proximity
- **Coordinates:** Added for slack locations and critical hardware

**Pain points:**
- 100+ poles = 100+ individual accessorizing decisions
- Lots of copy-pasting with minor variations
- Easy to miss rules or make mistakes
- Guesswork when rules overlap or conflict
- Time-consuming and mentally exhausting

**Status:** 🎯 **TARGET FOR AUTOMATION** (See Phase 2)

---

#### 5. Measurement & Distance Calculation
**What happens:**
- Use AutoCAD dimension tool to measure pole-to-pole distances
- Add dimension text between consecutive poles
- Calculate total cable lengths per segment
- Determine cable specifications based on capacity requirements
- Account for slack, service loops, and safety margins

**Purpose:** 
- Determine cable quantities for procurement
- Calculate project costs
- Validate design against span limits

**Pain points:**
- Manual clicking between every pole pair
- Repetitive dimension tool usage
- Manual aggregation of measurements
- Easy to miss segments or double-count

**Status:** 🎯 **TARGET FOR AUTOMATION** (See Phase 3)

---

#### 6. Documentation (Pole Schedule & Cable Schedule)
**What happens:**
- Create spreadsheet (pole schedule) with:
  - Pole coordinates (latitude, longitude)
  - Pole labels/IDs
  - Accessories per pole (quantities and types)
  - Special notes (ownership, conditions)
  
- Create cable schedule with:
  - Cable segment start/end points
  - Cable type and core count
  - Cable length per segment
  - Total cable quantities by type

**Pain points:**
- Manual data entry from AutoCAD to spreadsheet
- Copy-paste errors
- Inconsistent formatting
- Time-consuming for large networks (100+ poles)

**Status:** 🎯 **TARGET FOR AUTOMATION** (See Phase 3)

---

#### 7. FTTH-Specific Design
**What happens:**
- Determine FDT (Fiber Distribution Terminal) size based on total homes passed
- Position FDT cabinet through field survey (requires optimal location assessment)
- Cluster houses into service groups:
  - **SDUs (Single Dwelling Units):** Grouped in clusters of 12, 24, or 48
  - **MDUs (Multiple Dwelling Units):** Each MDU gets dedicated FAT(s), may need multiple FATs per building
- Place FATs (Fiber Access Terminals) to serve clusters:
  - FAT must be within 120m drop cable distance from all served houses
  - FAT size determined by cluster size (8-port, 16-port, 24-port, etc.)
- Position JBs (Joint Boxes) for cable splicing and distribution
- Route feeder cables from FDT to FATs via pole network
- Determine cable specifications:
  - Core count based on downstream demand
  - Cable type (ADSS for aerial, armored for underground)
- Add descriptive annotations to all infrastructure:
  - Cables: "48C ADSS 43HH" (48-core cable serving 43 homes)
  - FATs: "FAT-24 (24HH)" (24-port FAT serving 24 homes)
  - FDTs: "FDT-288 (500HP)" (288-fiber FDT serving 500 homes passed)
- Color-code elements by specification (core count, capacity tier)

**Design constraints:**
- Maximum drop cable length: 120m from FAT to customer
- Clustering efficiency: Prefer filling FATs to rated capacity
- Cable routing: Follow pole network, minimize total cable length
- Split ratios: Maintain proper optical budget
- Accessibility: FATs should be serviceable from road/pole
- Future expansion: Leave spare capacity for growth

**Pain points:**
- **No standardized rules:** Each senior designer has personal preferences and heuristics
- **Complex spatial optimization:** Balancing cluster sizes, drop distances, cable paths
- **Multiple valid solutions:** Hard to know which design is "best"
- **Trial and error:** Often need to iterate placement several times
- **Data quality issues:** Survey data has duplicates, missing descriptions, errors
- **Cognitive load:** Keeping track of constraints while designing

**Status:** 🎯 **TARGET FOR AUTOMATION** (See Phase 4 - most complex phase)

---

#### 8. Output Generation
**What happens:**
- Generate High-Level Design (HLD) on Google Earth Pro
- Generate Low-Level Design (LLD) on AutoCAD
- Export polished PDFs for distribution to:
  - Construction teams
  - Project managers
  - Procurement teams
  - Client stakeholders

**Current state:** Manual PDF generation

---

## Phase 1: Building & Road Extraction (COMPLETED)

### Problem Statement
Manually tracing building footprints and roads on Google Earth Pro was consuming hours per design and provided minimal value. This task was purely mechanical and didn't require design expertise.

### Solution Implemented
Built a web application that automatically extracts and aggregates building and road data from multiple authoritative sources.

### Technical Implementation

**Data Sources:**
- Google Open Buildings Dataset
- Microsoft Building Footprints
- OpenStreetMap (roads, landmarks, place names)

**Technology Stack:**
- **Backend:** FastAPI (Python)
- **Frontend:** Vanilla JavaScript
- **Geospatial Processing:** GeoPandas, Fiona, GDAL
- **Data Format Handling:** KMZ ↔ GeoJSON conversion

**User Workflow:**
1. User uploads KMZ file containing survey data (poles, cables, initial measurements)
2. Tool converts KMZ to GeoJSON
3. Tool visualizes design on interactive web map
4. User draws Area of Interest (AOI) polygon around the design area
5. User runs analysis
6. Tool aggregates data from multiple sources within AOI:
   - Building footprints (deduplicated and merged)
   - Road networks with classifications
   - Place names and landmarks
7. User exports results as KMZ
8. User imports KMZ into Google Earth Pro and continues design work

**Key Features:**
- Automatic deduplication of overlapping building data
- Spatial filtering based on user-defined AOI
- Format conversion (KMZ/GeoJSON) for interoperability
- Visualization for validation before export

### Impact
- **Time saved:** ~X hours per design (estimate: 2-4 hours)
- **Improved accuracy:** Using authoritative datasets vs. manual tracing
- **Team adoption:** Tool is being used by entire team
- **Eliminated low-value work:** No more manual tracing sessions

### Lessons Learned
- Data quality from different sources varies significantly
- GeoJSON is better for programmatic processing than KMZ
- Users prefer staying in familiar tools (Google Earth Pro) for final review
- Building tools that fit into existing workflow (not replacing it) drives adoption

---

## Phase 2: Pole Accessorizing Automation (PLANNED)

### Problem Statement
Accessorizing 100+ poles manually is time-consuming, error-prone, and follows predictable rules. The logic is deterministic but tedious to execute repeatedly.

### Solution Approach
Build a rules engine that automatically determines required accessories for each pole based on network topology, geometry, and contextual factors.

### Rule Categories

#### 1. Geometric Rules (Topology-Based)
**Corner Detection:**
- Calculate bearing between consecutive pole segments
- If bearing change > threshold (e.g., 15-30 degrees), pole is a corner
- **Action:** Add 2x tension clamps

**Span Distance Rules:**
- Calculate distance between consecutive poles
- For FTTB: If distance > threshold OR pole is every 3rd pole → Add tangent
- For FTTH: If distance > threshold OR pole is every 2nd pole → Add J-hook

#### 2. Infrastructure Crossing Rules
**Road Crossings:**
- Check if cable segment between poles intersects road geometry
- **Action:** Add:
  - 20m slack
  - Slack storage hardware
  - Downlead
  - UPB (Underground Protection Box)
  - Store slack coordinates for documentation

**Other Crossings:**
- Railway crossings (similar rules, different clearances)
- Water body crossings (may require special hardware)

#### 3. Ownership & Environmental Rules
**Third-Party Poles:**
- Check pole ownership attribute
- **Action:** Add rental marker/identifier

**Electrical Equipment Proximity:**
- Check if pole has electrical equipment (transformer, breaker)
- **Action:** Add isolation brackets or increased clearance hardware

**Pole Type:**
- Wooden vs. concrete vs. steel
- **Action:** Select appropriate mounting hardware

#### 4. Network Type Rules
**FTTB (Fiber to the Building):**
- Use tangents for cable support
- Larger spacing between support hardware

**FTTH (Fiber to the Home):**
- Use J-hooks for cable support
- Closer spacing for lighter cables

### Technical Implementation Plan

**Input Data Required:**
- Pole coordinates (lat, lon)
- Pole sequence (network topology/order)
- Pole attributes (ownership, equipment, type)
- Road geometries (from Phase 1 tool)
- Network type (FTTB/FTTH)
- Cable route geometry

**Processing Steps:**

```
1. Load pole network as graph structure (nodes = poles, edges = cable segments)
2. For each pole in sequence:
   a. Calculate geometric properties (bearing to prev/next, distance to neighbors)
   b. Check for infrastructure intersections (roads, railways, water)
   c. Apply rule engine to determine accessories
   d. Annotate pole with accessory list
3. Generate pole schedule spreadsheet
4. Export annotated KMZ with accessory data in descriptions
```

**Output:**
- KMZ file with poles annotated with accessory requirements
- Pole schedule spreadsheet (coordinates, labels, accessories)
- Summary report (total accessory counts by type)

### Expected Benefits
- **Time saved:** ~X hours per design (estimate: 3-5 hours for 100-pole network)
- **Consistency:** Eliminate human error in applying rules
- **Documentation:** Automatic pole schedule generation
- **Audit trail:** Clear rule application logic for validation

### Challenges to Address
- **Conflicting rules:** What if pole is both a corner AND a road crossing?
  - Solution: Priority system or additive rules
- **Edge cases:** First/last pole in network, junctions, branch points
  - Solution: Special handling in rule engine
- **Rule variations:** Different regions/teams may have slightly different rules
  - Solution: Configurable rule parameters

---

## Phase 3: Measurement & Cable Scheduling (PLANNED)

### Problem Statement
Using AutoCAD dimension tool to measure pole-to-pole distances is repetitive and provides no design value. The data exists in coordinates—calculations should be automatic.

### Solution Approach
Calculate all distances programmatically from geospatial coordinates and auto-generate cable schedules.

### Technical Implementation Plan

**Input Data:**
- Pole coordinates (from network topology)
- Cable routing paths
- Downstream demand per segment (homes/businesses served)

**Distance Calculations:**
- Use Haversine formula for lat/lon coordinates
- Account for:
  - Direct pole-to-pole distance
  - Cable slack allowances (typically 2-5% extra)
  - Service loops at terminations
  - Vertical rise (pole height) if data available

**Cable Specification Logic:**
```
For each cable segment:
1. Count downstream homes/services
2. Calculate required fiber count (homes × fibers per home / split ratio)
3. Select standard cable size (round up to 12, 24, 48, 72, 96, 144, etc.)
4. Apply safety margin for future growth
5. Assign cable type based on deployment (ADSS for aerial, armored for underground)
```

**Output Generation:**
- **Cable Schedule Spreadsheet:**
  - Segment ID (from_pole → to_pole)
  - Distance (meters)
  - Cable type and core count
  - Homes served
  - Special notes (road crossing, slack location)
  
- **Summary Totals:**
  - Total cable length by type/size
  - Total accessories by type
  - Cost estimation (if unit prices available)

**Integration with Phase 2:**
- Combine accessory data with measurement data
- Single comprehensive pole schedule with all information

### Expected Benefits
- **Time saved:** ~X hours per design (estimate: 2-3 hours)
- **Accuracy:** Eliminate measurement errors
- **Instant updates:** Recalculate if design changes
- **Cost visibility:** Immediate material quantity estimates

---

## Phase 4: FTTH Design Recommendation Engine (PLANNED)

### Problem Statement
FTTH design is the most complex and least standardized part of the workflow. Each senior designer has their own preferences and heuristics, making it difficult to automate with rigid rules. The goal is not to replace designers but to **reduce their workload** by generating viable design alternatives they can choose from.

### Solution Philosophy
Build a **recommendation engine** that generates multiple valid design options based on constraints and optimization strategies. Think "design autocomplete" rather than "design automation."

### Design Problem Decomposition

FTTH design is fundamentally a **constrained optimization problem** with these components:

1. **Clustering:** Group houses into service clusters
2. **Facility location:** Place FATs/JBs optimally
3. **Routing:** Connect FDT → FATs via pole network
4. **Capacity planning:** Size cables and equipment
5. **Annotation:** Document design decisions

---

### Step 1: Data Cleaning & Validation

**Problem:** Survey data often has quality issues that break downstream processing.

**Common issues:**
- Duplicate house entries (same coordinates, different labels)
- Missing descriptions ("House" vs "2-story residential")
- Inconsistent naming conventions
- Incorrect coordinates (typos, wrong decimal places)
- MDU miscounted as multiple SDUs

**Cleaning Logic:**
```
1. Spatial deduplication:
   - If two houses within 5m, check if duplicate
   - Merge entries if descriptions similar

2. Description standardization:
   - Extract house count from description
   - Classify as SDU vs MDU
   - Flag missing data for review

3. Coordinate validation:
   - Check if coordinates fall within expected bounds
   - Flag outliers for manual review

4. Count reconciliation:
   - Compare house count in descriptions vs. spatial count
   - Report discrepancies
```

**Output:** Clean dataset ready for clustering

---

### Step 2: House Clustering

**Objective:** Group houses into service clusters that can be served by a single FAT.

**Constraints:**
- Maximum drop cable distance: 120m from FAT to any house in cluster
- Preferred cluster sizes: 12, 24, 48 (matches FAT port counts)
- Avoid splitting natural groupings (e.g., apartment buildings)

**Algorithm Options:**

**Option A: DBSCAN (Density-Based Clustering)**
- Pros: Handles irregular shapes, finds natural clusters
- Cons: Doesn't enforce max cluster size
- Use case: Initial clustering, then split oversized clusters

**Option B: K-Means with Constraints**
- Pros: Can enforce cluster size targets
- Cons: Assumes spherical clusters (not always true)
- Use case: Areas with uniform house distribution

**Option C: Hierarchical Clustering**
- Pros: Builds cluster hierarchy, easy to visualize
- Cons: Computationally expensive for large datasets
- Use case: Complex topology with sub-clusters

**Implementation Strategy:**
```
1. Run DBSCAN with eps=120m (max drop distance)
2. For each cluster:
   - If size ≤ 48: Accept cluster
   - If size > 48: Split into sub-clusters of ~24 each
3. For undersized clusters (<8 houses):
   - Check if can merge with neighbor without violating distance constraint
4. Special handling for MDUs:
   - Each MDU building is its own cluster
   - Size FAT(s) based on unit count
```

**Output:** Houses grouped into clusters with predicted FAT requirements

---

### Step 3: FAT Placement Optimization

**Objective:** For each cluster, find optimal FAT location(s) on the pole network.

**Constraints:**
- FAT must be pole-mounted (or at approved ground location)
- All houses in cluster must be within 120m drop distance
- FAT should be accessible for maintenance
- Prefer main road poles over side street poles

**Placement Algorithm:**
```
For each cluster:
1. Get all poles within service area
2. For each candidate pole:
   a. Calculate max drop distance to farthest house in cluster
   b. If max_distance ≤ 120m → valid candidate
   c. Calculate placement score based on:
      - Total drop cable length (minimize)
      - Pole accessibility (prefer main roads)
      - Pole loading (avoid overloading single pole)
      - Proximity to FDT (shorter feeder cable)
3. Rank candidates by score
4. Return top 3-5 options
```

**Scoring Function Example:**
```
score = w1 × (1 / total_drop_length) +
        w2 × accessibility_factor +
        w3 × (1 / distance_to_FDT) +
        w4 × pole_capacity_available

Where w1, w2, w3, w4 are tunable weights
```

**Output:** Ranked list of FAT placement options per cluster

---

### Step 4: Cable Routing (Feeder Cables)

**Objective:** Route feeder cables from FDT to each FAT via the pole network.

**Approach:** This is a **shortest path problem** on a graph.

**Graph Structure:**
- **Nodes:** Poles, FDT, FAT locations
- **Edges:** Cable spans between poles
- **Edge weights:** Distance (or cost function)

**Algorithm:** Dijkstra's shortest path or A* with heuristic

**Implementation:**
```python
import networkx as nx

# Build pole network graph
G = nx.Graph()
for pole in poles:
    G.add_node(pole.id, pos=(pole.lat, pole.lon))

for connection in pole_connections:
    distance = calculate_distance(connection.start, connection.end)
    G.add_edge(connection.start, connection.end, weight=distance)

# Find route from FDT to each FAT
for fat in fats:
    path = nx.shortest_path(G, source=fdt.nearest_pole, target=fat.pole, weight='weight')
    cable_route = reconstruct_route(path)
```

**Enhancements:**
- Add penalties for road crossings (increases weight)
- Prefer main roads (decreases weight)
- Consider existing cable paths (trenching already done)

**Output:** Cable routes with distances and waypoints

---

### Step 5: Cable Sizing & Specification

**Objective:** Determine required fiber count and cable specifications.

**Calculation:**
```
For each cable segment:
1. Count total downstream homes served by this segment
2. Calculate fibers needed:
   fibers_required = homes × fibers_per_home / split_ratio
   
   Example: 
   - 48 homes, 2 fibers per home, 1:8 split ratio
   - fibers_required = 48 × 2 / 8 = 12 fibers

3. Round up to standard cable size: 12, 24, 48, 72, 96, 144, 288
4. Add growth margin (e.g., 20% spare capacity)
5. Select cable type:
   - Aerial: ADSS (All-Dielectric Self-Supporting)
   - Underground: Armored or duct cable
```

**Cascade Effect:**
- Cables closer to FDT carry more fibers (aggregate demand)
- Cables closer to FATs carry fewer fibers (local demand)

**Output:** Cable specifications for each segment

---

### Step 6: FDT Sizing

**Objective:** Determine FDT cabinet size based on total homes passed.

**Logic:**
```
1. Count total homes in entire design area
2. Calculate total fiber terminations needed:
   - FTTH: ~2 fibers per home
   - Include splice margin (20%)
3. Select FDT size: 144, 288, 576, 864, 1152 fibers
4. Consider future expansion (next 5-10 years)
```

**Note:** FDT location is determined by field survey (cannot be automated without site visit), but size can be calculated.

**Output:** FDT specification

---

### Step 7: Design Variant Generation

**Objective:** Generate multiple valid design alternatives using different optimization strategies.

**Variant Strategies:**

**Strategy 1: Minimize Total Cable Length**
- Objective: Lowest material cost
- Approach: Aggressive clustering, shortest paths
- Trade-off: May result in awkward FAT placements

**Strategy 2: Minimize Component Count**
- Objective: Fewer FATs, simpler network
- Approach: Maximize FAT capacity utilization (fill to 48 ports)
- Trade-off: Longer drop cables, may approach 120m limit

**Strategy 3: Balanced Approach**
- Objective: Balance cost vs. serviceability
- Approach: Moderate cluster sizes (~24), accessible FAT locations
- Trade-off: Middle ground on all metrics

**Strategy 4: Mimic Senior Designer Patterns**
- Objective: Match established design preferences
- Approach: Learn heuristics from historical designs
- Trade-off: Requires training data from past projects

**Implementation:**
```
For each strategy:
1. Apply clustering algorithm with strategy-specific parameters
2. Place FATs according to strategy priorities
3. Route cables using strategy-specific cost function
4. Calculate design metrics:
   - Total cable length (meters)
   - Total component count (FATs, JBs, splitters)
   - Estimated cost
   - Average drop cable length
   - Buildability score (subjective, based on complexity)
5. Present variants side-by-side for comparison
```

**Output:** 3-5 design variants with comparative metrics

---

### Step 8: Auto-Annotation & Color Coding

**Objective:** Add descriptive metadata to all infrastructure for documentation and visualization.

**Annotation Format:**

**Cables:**
- Format: `{core_count}C {cable_type} {homes_served}HH`
- Example: `48C ADSS 43HH` = 48-core ADSS cable serving 43 homes
- Color code by core count:
  - 12C: Green
  - 24C: Blue
  - 48C: Orange
  - 72C+: Red

**FATs:**
- Format: `FAT-{port_count} ({homes_served}HH)`
- Example: `FAT-24 (24HH)` = 24-port FAT serving 24 homes
- Color code by capacity:
  - 8-16 port: Yellow
  - 24 port: Cyan
  - 48 port: Magenta

**FDTs:**
- Format: `FDT-{fiber_count} ({homes_passed}HP)`
- Example: `FDT-288 (500HP)` = 288-fiber FDT serving 500 homes passed
- Color: Purple (consistent)

**JBs (Joint Boxes):**
- Format: `JB-{splice_count} ({purpose})`
- Example: `JB-12 (Branch)` = Joint box with 12 splices for branching
- Color: Gray

**Implementation:**
```python
def annotate_cable(cable_segment):
    description = f"{cable_segment.core_count}C {cable_segment.cable_type} {cable_segment.homes_served}HH"
    color = get_color_by_core_count(cable_segment.core_count)
    
    return {
        "description": description,
        "color": color,
        "metadata": {
            "length": cable_segment.length,
            "from": cable_segment.start_point,
            "to": cable_segment.end_point
        }
    }
```

**Output:** Fully annotated KMZ with color-coded elements

---

### User Interface & Workflow

**Step-by-step user experience:**

1. **Upload Survey Data:**
   - User uploads KMZ with house locations, pole network, FDT position
   - Tool validates and cleans data, reports issues

2. **Review Cleaned Data:**
   - User sees map with cleaned houses, clusters, potential duplicates flagged
   - User can manually correct issues before proceeding

3. **Generate Design Variants:**
   - User clicks "Generate Designs"
   - Tool runs all optimization strategies in parallel
   - Progress indicator shows: Clustering → FAT placement → Routing → Sizing

4. **Compare Variants:**
   - User sees side-by-side comparison of 3-5 design options
   - Metrics shown: Total cable length, component count, cost estimate, complexity score
   - Interactive map shows each design visually

5. **Select & Refine:**
   - User selects preferred design variant
   - User can manually adjust:
     - FAT locations (drag to different pole)
     - Cluster assignments (reassign houses)
     - Cable routes (pick alternate path)
   - Tool recalculates metrics after each change

6. **Export:**
   - User exports selected design as annotated KMZ
   - Tool generates:
     - Pole schedule spreadsheet
     - Cable schedule spreadsheet
     - Bill of materials (BOM)
     - Design summary report

**Design Philosophy:**
- **Transparent:** Show user why decisions were made (which rules applied)
- **Flexible:** Allow manual overrides at every step
- **Iterative:** Easy to tweak and regenerate
- **Educational:** Help junior designers learn by seeing multiple approaches

---

### Machine Learning Potential (Future Enhancement)

Once sufficient historical design data is collected:

**Pattern Learning:**
- Train model on past designs to learn implicit designer preferences
- Features: Topology characteristics, cluster patterns, routing choices
- Output: Probability distribution over design decisions

**Anomaly Detection:**
- Flag unusual designs that deviate from historical patterns
- Alert: "This design has unusually long drop cables - is this intentional?"

**Cost Prediction:**
- Train regression model on actual build costs vs. design parameters
- Improve cost estimation accuracy over time

**Note:** This is a future enhancement - initial version uses rules-based approach.

---

### Expected Benefits

**Quantitative:**
- **Time saved:** ~X hours per FTTH design (estimate: 8-15 hours for complex area)
- **Design alternatives:** 3-5 options generated in minutes vs. days
- **Consistency:** Eliminate forgot-to-check-a-constraint errors

**Qualitative:**
- **Learning tool:** Junior designers see multiple valid approaches
- **Confidence:** Designers can validate their intuition against algorithm
- **Strategic focus:** Spend time on complex edge cases, not routine layouts
- **Better outcomes:** Explore more alternatives = higher chance of optimal solution

---

### Challenges & Mitigation Strategies

**Challenge 1: Design Preferences Vary**
- **Issue:** No single "correct" design; different designers prefer different approaches
- **Mitigation:** Generate multiple variants representing different philosophies; let user choose

**Challenge 2: Data Quality**
- **Issue:** Survey data has errors, missing info, inconsistencies
- **Mitigation:** Robust data cleaning pipeline; flag issues for manual review; graceful degradation

**Challenge 3: Complex Edge Cases**
- **Issue:** Some scenarios don't fit standard rules (irregular terrain, special requirements)
- **Mitigation:** Always allow manual override; design for human-in-the-loop workflow

**Challenge 4: FDT Location Unknown**
- **Issue:** FDT position requires field survey; can't be automated
- **Mitigation:** Accept FDT location as input; user marks it after site visit

**Challenge 5: Algorithm Validation**
- **Issue:** How do we know generated designs are good?
- **Mitigation:** 
  - Start with simple scenarios, validate against known-good designs
  - Pilot with experienced designers reviewing outputs
  - Collect feedback and iterate

**Challenge 6: Performance at Scale**
- **Issue:** Large areas (1000+ houses) may be slow to process
- **Mitigation:** 
  - Optimize algorithms (use spatial indexing, caching)
  - Show progress indicators
  - Allow user to subdivide large areas

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  (Web Browser - Interactive Map, Forms, Visualization)       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────▼────────────────────────────────────┐
│                      Backend API Layer                       │
│                      (FastAPI - Python)                      │
├─────────────────────────────────────────────────────────────┤
│  • File Upload/Download (KMZ ↔ GeoJSON conversion)         │
│  • Data Validation & Cleaning                                │
│  • Orchestration of analysis pipelines                       │
│  • Result caching and session management                     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│  Geospatial  │  │   Network   │
│  Geospatial  │  │   Network   │  │ Optimization│
│  Processing  │  │   Analysis  │  │   Engine    │
│    Module    │  │    Module   │  │             │
└──────────────┘  └─────────────┘  └─────────────┘
│ GeoPandas    │  │  NetworkX   │  │ scikit-learn│
│ Shapely      │  │  Graph Algo │  │ PuLP/OR-Tools│
│ GDAL/Fiona   │  │  Routing    │  │ Clustering  │
│ Spatial Index│  │  Topology   │  │ Optimization│
└──────────────┘  └─────────────┘  └─────────────┘
```

### Technology Stack

**Backend:**
- **Framework:** FastAPI (async, high-performance REST API)
- **Language:** Python 3.9+
- **Geospatial Libraries:**
  - GeoPandas: Geospatial data manipulation
  - Shapely: Geometric operations
  - Fiona: File I/O for geospatial formats
  - GDAL: Format conversion and coordinate transformations
  - PyProj: Coordinate reference system transformations
  - RTRee: Spatial indexing for fast queries
- **Network Analysis:**
  - NetworkX: Graph algorithms, shortest path, topology analysis
- **Optimization & ML:**
  - scikit-learn: Clustering algorithms (DBSCAN, K-means)
  - PuLP or Google OR-Tools: Linear programming, constraint satisfaction
  - NumPy/Pandas: Numerical computing and data manipulation
- **Data Validation:**
  - Pydantic: Type validation and serialization

**Frontend:**
- **Current:** Vanilla JavaScript (lightweight, no build step)
- **Future consideration:** React or Vue.js (if complexity increases)
- **Mapping Library:** 
  - Leaflet.js or Mapbox GL JS: Interactive map visualization
  - Option to integrate Google Earth Engine API
- **UI Components:** 
  - Bootstrap or Tailwind CSS for responsive design
  - Chart.js for metrics visualization

**Data Formats:**
- **Input:** KMZ (Keyhole Markup Language Zipped)
- **Processing:** GeoJSON (easier to manipulate programmatically)
- **Output:** KMZ (for Google Earth Pro compatibility)
- **Documentation:** CSV/Excel (pole schedules, cable schedules, BOMs)

**Infrastructure:**
- **Development:** Local development server
- **Deployment (future):** 
  - Docker containers for reproducibility
  - Cloud hosting (AWS/GCP/Azure) or internal server
  - Database (PostgreSQL + PostGIS) for historical design storage

---

### Data Flow Architecture

```
┌──────────────┐
│  User Upload │
│  (KMZ file)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  File Processing Pipeline            │
├──────────────────────────────────────┤
│  1. KMZ → KML extraction             │
│  2. KML → GeoJSON conversion         │
│  3. Coordinate system normalization  │
│  4. Schema validation                │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Data Cleaning & Validation          │
├──────────────────────────────────────┤
│  1. Spatial deduplication            │
│  2. Description parsing              │
│  3. Coordinate validation            │
│  4. Topology validation              │
│  5. Error reporting                  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Analysis & Processing               │
├──────────────────────────────────────┤
│  PHASE 1: Building/Road Extraction   │
│  - Query external data sources       │
│  - Spatial filtering by AOI          │
│  - Data aggregation & merging        │
│                                      │
│  PHASE 2: Pole Accessorizing         │
│  - Build network graph               │
│  - Apply rule engine                 │
│  - Generate accessory assignments    │
│                                      │
│  PHASE 3: Measurement & Scheduling   │
│  - Calculate distances               │
│  - Determine cable specs             │
│  - Generate schedules                │
│                                      │
│  PHASE 4: FTTH Design Generation     │
│  - House clustering                  │
│  - FAT placement optimization        │
│  - Cable routing                     │
│  - Design variant generation         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Result Generation                   │
├──────────────────────────────────────┤
│  1. Annotate features                │
│  2. Apply color coding               │
│  3. GeoJSON → KML conversion         │
│  4. KML → KMZ packaging              │
│  5. Generate spreadsheets            │
│  6. Create summary reports           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│ User Download│
│  (KMZ +      │
│   Schedules) │
└──────────────┘
```

---

### API Endpoints Structure

**File Management:**
```
POST   /api/upload          - Upload KMZ file
GET    /api/projects/{id}   - Get project data
DELETE /api/projects/{id}   - Delete project
```

**Phase 1 - Building/Road Extraction:**
```
POST   /api/extract-buildings  - Extract buildings in AOI
POST   /api/extract-roads      - Extract roads in AOI
POST   /api/extract-landmarks  - Extract place names
```

**Phase 2 - Pole Accessorizing:**
```
POST   /api/accessorize        - Generate pole accessories
GET    /api/accessory-rules    - Get current rule configuration
PUT    /api/accessory-rules    - Update rule parameters
```

**Phase 3 - Measurement:**
```
POST   /api/calculate-distances - Calculate pole-to-pole distances
POST   /api/generate-cable-schedule - Create cable schedule
POST   /api/generate-pole-schedule - Create pole schedule
```

**Phase 4 - FTTH Design:**
```
POST   /api/clean-survey-data    - Clean and validate house data
POST   /api/cluster-houses       - Generate house clusters
POST   /api/generate-designs     - Create design variants
GET    /api/designs/{id}/metrics - Get design comparison metrics
PUT    /api/designs/{id}/adjust  - Manual design adjustments
```

**Export:**
```
GET    /api/export/kmz/{id}      - Download annotated KMZ
GET    /api/export/schedules/{id} - Download Excel schedules
GET    /api/export/report/{id}   - Download PDF report
```

---

### Data Models

**Project:**
```json
{
  "id": "uuid",
  "name": "Project Alpha - Phase 1",
  "created_at": "2025-09-29T10:00:00Z",
  "status": "processing|completed|failed",
  "area_of_interest": {
    "type": "Polygon",
    "coordinates": [[[lon, lat], ...]]
  },
  "metadata": {
    "total_poles": 150,
    "total_houses": 500,
    "network_type": "FTTH",
    "region": "Juja, Kenya"
  }
}
```

**Pole:**
```json
{
  "id": "P001",
  "coordinates": {"lat": -1.1234, "lon": 36.9876},
  "type": "wooden|concrete|steel",
  "owner": "company|third_party",
  "has_electrical_equipment": false,
  "accessories": [
    {"type": "tension_clamp", "quantity": 2, "reason": "corner"},
    {"type": "j_hook", "quantity": 1, "reason": "span_distance"}
  ],
  "neighbors": {
    "previous": "P000",
    "next": "P002"
  }
}
```

**House/Building:**
```json
{
  "id": "H001",
  "coordinates": {"lat": -1.1234, "lon": 36.9876},
  "type": "SDU|MDU",
  "unit_count": 1,
  "description": "2-story residential",
  "cluster_id": "C01",
  "assigned_fat": "FAT-01"
}
```

**Cluster:**
```json
{
  "id": "C01",
  "house_ids": ["H001", "H002", ..., "H024"],
  "size": 24,
  "centroid": {"lat": -1.1234, "lon": 36.9876},
  "recommended_fats": [
    {
      "pole_id": "P045",
      "size": 24,
      "score": 0.92,
      "max_drop_distance": 95,
      "reasoning": "Central location, main road access"
    }
  ]
}
```

**Cable Segment:**
```json
{
  "id": "CS001",
  "from": "P001",
  "to": "P002",
  "distance": 45.7,
  "cable_type": "ADSS",
  "core_count": 48,
  "homes_served": 43,
  "description": "48C ADSS 43HH",
  "color": "#FF6600",
  "accessories": ["slack_20m"]
}
```

**Design Variant:**
```json
{
  "id": "DV001",
  "strategy": "minimize_cable_length",
  "metrics": {
    "total_cable_length": 2450,
    "total_fats": 18,
    "total_cost_estimate": 125000,
    "avg_drop_distance": 67,
    "complexity_score": 0.72
  },
  "clusters": [...],
  "cable_routes": [...],
  "bom": {
    "cables": {"48C": 1200, "24C": 800, "12C": 450},
    "fats": {"24port": 15, "48port": 3},
    "accessories": {...}
  }
}
```

---

## Impact Metrics

### Current Status (Phase 1 Complete)

**Time Savings:**
- Manual tracing time per project: ~3-4 hours
- Automated extraction time: ~2-5 minutes
- **Time saved per project:** ~3.5 hours
- **Monthly projects:** ~10
- **Total monthly time saved:** ~35 hours

**Quality Improvements:**
- **Accuracy:** Using authoritative datasets vs. manual tracing
- **Consistency:** Same data sources across all projects
- **Completeness:** Less likely to miss buildings or roads

**Team Adoption:**
- **Users:** Entire planning team (X people)
- **Usage rate:** ~100% for new projects
- **Feedback:** Positive (manager confirmed "tool is nice")

---

### Projected Impact (All Phases Complete)

**Phase 2 - Pole Accessorizing:**
- Estimated time saved: ~3-5 hours per 100-pole network
- Error reduction: ~80% fewer accessory omissions
- Documentation: Auto-generated pole schedules

**Phase 3 - Measurement & Scheduling:**
- Estimated time saved: ~2-3 hours per project
- Accuracy improvement: Eliminate measurement errors
- Instant recalculation if design changes

**Phase 4 - FTTH Design:**
- Estimated time saved: ~8-15 hours per complex FTTH area
- Design alternatives: 3-5 variants generated in minutes vs. days
- Quality: Explore more options = better outcomes

**Total Potential:**
- **Time saved per project:** ~20-25 hours (from ~30 hours to ~5-10 hours)
- **Efficiency gain:** ~65-75% reduction in design time
- **Value shift:** From mechanical execution to strategic review and decision-making

---

### Business Value

**Cost Savings:**
- Designer time is expensive (salary + overhead)
- Faster project completion = more projects per month
- Reduced errors = less rework and field corrections

**Quality Improvements:**
- More design alternatives explored = better optimization
- Consistent rule application = fewer build issues
- Better documentation = easier construction and maintenance

**Strategic Benefits:**
- Designers focus on complex problems, not repetitive tasks
- Junior designers learn faster (see multiple approaches)
- Knowledge capture (design logic encoded in rules, not just in people's heads)
- Scalability (can handle larger/more complex projects)

**Competitive Advantage:**
- Faster proposal turnaround for new projects
- More accurate cost estimates (better cable calculations)
- Higher quality designs (optimization-based)

---

## Challenges & Considerations

### Technical Challenges

**1. Data Quality & Consistency**
- **Problem:** Survey data varies in quality, format, completeness
- **Impact:** Garbage in, garbage out - poor data = poor automation results
- **Mitigation:** 
  - Robust data cleaning pipeline with validation
  - Clear error reporting for manual correction
  - Data quality checklist for field teams

**2. Rule Complexity & Conflicts**
- **Problem:** Design rules can conflict or have edge cases
- **Impact:** Algorithm may produce invalid or suboptimal results
- **Mitigation:**
  - Rule priority system
  - Validation checks before output
  - Allow manual override at every step

**3. Performance at Scale**
- **Problem:** Large networks (1000+ poles, 5000+ houses) may be slow
- **Impact:** Poor user experience, timeouts
- **Mitigation:**
  - Optimize algorithms (spatial indexing, caching)
  - Progress indicators and async processing
  - Option to subdivide large areas

**4. Integration with Existing Tools**
- **Problem:** Designs still need to go into AutoCAD for final formatting
- **Impact:** Not fully automated end-to-end
- **Mitigation:**
  - Export formats compatible with AutoCAD import
  - Consider AutoCAD API integration (future)
  - Focus on automation of analysis, not final drawing

**5. Algorithm Validation**
- **Problem:** How do we know generated designs are good?
- **Impact:** Designers may not trust automation
- **Mitigation:**
  - Start with known-good test cases
  - Pilot with experienced designers reviewing
  - Compare generated designs to manual designs
  - Iterative improvement based on feedback

---

### Organizational Challenges

**1. Change Management**
- **Problem:** "We've always done it this way" resistance
- **Impact:** Low adoption despite tool availability
- **Mitigation:**
  - Demonstrate time savings with real examples
  - Start with volunteers/early adopters
  - Show, don't tell (demos more effective than explanations)
  - Position as "assistant" not "replacement"

**2. Manager Skepticism**
- **Problem:** Manager says automation "not possible"
- **Impact:** Lack of support, no resources allocated
- **Mitigation:**
  - Build prototype to prove it works
  - Quantify impact (hours saved, errors reduced)
  - Frame as innovation initiative
  - Show incremental value (Phase 1 already successful)

**3. Diverse Design Preferences**
- **Problem:** Different designers have different styles
- **Impact:** No single "right" answer for algorithm
- **Mitigation:**
  - Recommendation engine approach (multiple options)
  - Configurable parameters for different styles
  - Learn from historical data (future ML enhancement)

**4. Knowledge Sharing**
- **Problem:** Design expertise lives in senior designers' heads
- **Impact:** Hard to encode all rules and heuristics
- **Mitigation:**
  - Collaborative rule development (interview designers)
  - Iterative refinement as new patterns discovered
  - Documentation of reasoning behind rules

**5. Tool Maintenance**
- **Problem:** Who maintains/updates the automation tools?
- **Impact:** Tools become outdated or break over time
- **Mitigation:**
  - Clear ownership and responsibility
  - Documentation for future developers
  - Modular architecture for easy updates
  - Version control and testing

---

### Risk Mitigation Strategy

**Risk: Algorithm produces unsafe/invalid designs**
- **Severity:** High
- **Mitigation:** 
  - Validation checks at every step
  - Human review required before construction
  - Conservative safety margins in calculations
  - Testing on historical known-good designs

**Risk: Data privacy/security concerns**
- **Severity:** Medium
- **Mitigation:**
  - No sensitive customer data in system (just coordinates)
  - Secure file handling (encrypted uploads)
  - Access control for project data
  - Compliance with company policies

**Risk: Tool becomes bottleneck (single point of failure)**
- **Severity:** Medium
- **Mitigation:**
  - Tool is additive, not replacement (can still do manual)
  - Offline fallback capabilities
  - Redundant deployment options
  - Export capabilities to preserve data

**Risk: Over-automation reduces learning for junior designers**
- **Severity:** Low-Medium
- **Mitigation:**
  - Tool explains reasoning behind decisions
  - Training mode that teaches rules
  - Graduated usage (manual first, then automated)
  - Encourage reviewing multiple design variants

---

## Next Steps & Roadmap

### Immediate Priorities (Next 1-3 Months)

**1. Phase 2 Development: Pole Accessorizing**
- [ ] Define complete rule set with senior designers
- [ ] Build rule engine architecture
- [ ] Implement geometric analysis (corners, crossings)
- [ ] Create pole schedule generator
- [ ] Test on 5-10 historical projects
- [ ] Validate against manual accessorizing
- [ ] Deploy to team for pilot testing

**2. Quantify Phase 1 Impact**
- [ ] Survey team on time savings
- [ ] Calculate total hours saved since deployment
- [ ] Document error reduction / quality improvements
- [ ] Create presentation for management

**3. Build Business Case for Phases 3-4**
- [ ] Estimate development time required
- [ ] Project ROI based on time savings
- [ ] Identify resource needs (if any)
- [ ] Propose timeline and milestones

---

### Medium-Term Goals (3-6 Months)

**4. Phase 3 Development: Measurement & Scheduling**
- [ ] Implement distance calculation engine
- [ ] Build cable specification logic
- [ ] Create cable schedule generator
- [ ] Integrate with Phase 2 (combined pole/cable schedules)
- [ ] Test and validate

**5. Phase 4 Initial Development: FTTH Design**
- [ ] Build data cleaning pipeline
- [ ] Implement clustering algorithms
- [ ] Create FAT placement optimizer
- [ ] Develop cable routing engine
- [ ] Test on simple FTTH scenarios

**6. User Interface Improvements**
- [ ] Better visualization of results
- [ ] Interactive design editing capabilities
- [ ] Comparison tools for design variants
- [ ] Export format customization

---

### Long-Term Vision (6-12 Months)

**7. Phase 4 Full Implementation**
- [ ] Complete FTTH recommendation engine
- [ ] Multi-variant generation
- [ ] Cost estimation integration
- [ ] Full annotation and color coding
- [ ] Production deployment

**8. Advanced Features**
- [ ] Historical design database
- [ ] Machine learning for preference learning
- [ ] Automated cost optimization
- [ ] Integration with procurement systems
- [ ] Mobile app for field data collection

**9. Platform Expansion**
- [ ] Support for FTTB designs
- [ ] Underground network design
- [ ] Wireless network planning (if applicable)
- [ ] Capacity planning tools
- [ ] Network monitoring integration

---

### Success Criteria

**Phase 2 Success:**
- ✅ Accurately generates accessories for 95%+ of poles
- ✅ Saves 3+ hours per 100-pole network
- ✅ Adopted by 80%+ of team within 2 months

**Phase 3 Success:**
- ✅ Calculation accuracy matches manual within 1%
- ✅ Auto-generated schedules require minimal corrections
- ✅ Saves 2+ hours per project

**Phase 4 Success:**
- ✅ Generates valid FTTH designs for 80%+ of scenarios
- ✅ At least 1 of 3-5 variants acceptable to designer
- ✅ Saves 8+ hours per complex FTTH area
- ✅ Designers report increased confidence in design quality

**Overall Success:**
- ✅ Total design time reduced by 60%+
- ✅ Designer satisfaction improves (focus on strategy, not execution)
- ✅ Error rate in designs decreases
- ✅ Company can handle more projects with same team size

---

## Conclusion

This automation project represents a systematic approach to transforming fiber network design from a manual, repetitive process to an assisted, optimization-based workflow. By progressively automating the mechanical aspects of design, we free designers to focus on strategic thinking, complex problem-solving, and decision-making.

**Key Principles:**
1. **Augment, don't replace:** Tools assist human designers, not eliminate them
2. **Iterative development:** Build incrementally, validate continuously
3. **Transparency:** Show reasoning, allow overrides
4. **Measurable impact:** Track time saved, errors reduced, quality improved

**Current State:**
- Phase 1 complete and successfully deployed
- Proven value with building/road extraction automation
- Team adoption validates approach

**Future State:**
- End-to-end automation of routine design tasks
- Designers spend 70%+ time on strategy vs. 30% on execution
- Higher quality designs through optimization
- Faster project delivery without adding headcount

**Personal Growth:**
- Developing expertise in geospatial analysis, optimization, and software engineering
- Building portfolio of impactful automation projects
- Demonstrating value beyond traditional trainee expectations
- Positioning for roles in network planning automation, GIS engineering, or telecom software development

---

## Appendices

### Appendix A: Glossary of Terms

**Network Infrastructure:**
- **FTTH:** Fiber to the Home - fiber optic network extending to individual residences
- **FTTB:** Fiber to the Building - fiber to a building, copper for last connection
- **FDT:** Fiber Distribution Terminal - main distribution point for fiber network
- **FAT:** Fiber Access Terminal - local distribution point serving cluster of homes
- **JB:** Joint Box - enclosure for cable splicing and connections
- **SDU:** Single Dwelling Unit - individual house
- **MDU:** Multiple Dwelling Unit - apartment building, multiple homes

**Cable Types:**
- **ADSS:** All-Dielectric Self-Supporting - aerial fiber cable, no metallic elements
- **Core Count:** Number of fiber strands in a cable (12C, 24C, 48C, etc.)

**Accessories:**
- **Tension Clamp:** Hardware to secure cable at turns/corners
- **Tangent:** Cable support bracket for straight runs (FTTB)
- **J-Hook:** Cable support hook for straight runs (FTTH)
- **Slack:** Extra cable length for repairs/flexibility
- **UPB:** Underground Protection Box
- **Downlead/Uplead:** Vertical cable sections

**Design Outputs:**
- **HLD:** High-Level Design - overview in Google Earth Pro
- **LLD:** Low-Level Design - detailed drawings in AutoCAD
- **KMZ:** Keyhole Markup Language Zipped - Google Earth file format
- **Pole Schedule:** Spreadsheet listing all poles with accessories and specs
- **Cable Schedule:** Spreadsheet listing all cable segments with specs
- **BOM:** Bill of Materials - list of all components needed for construction

---

### Appendix B: Technical References

**Geospatial Libraries:**
- GeoPandas: https://geopandas.org/
- Shapely: https://shapely.readthedocs.io/
- GDAL: https://gdal.org/
- NetworkX: https://networkx.org/

**Optimization Tools:**
- scikit-learn: https://scikit-learn.org/
- PuLP: https://coin-or.github.io/pulp/
- Google OR-Tools: https://developers.google.com/optimization

**Data Sources:**
- Google Open Buildings: https://sites.research.google/open-buildings/
- Microsoft Building Footprints: https://github.com/microsoft/GlobalMLBuildingFootprints
- OpenStreetMap: https://www.openstreetmap.org/

---

### Appendix C: Change Log

**Version 1.0 - September 2025**
- Initial document creation
- Phase 1 (Building/Road Extraction) complete and deployed
- Phases 2-4 planning and architecture defined

**Future Updates:**
- [ ] Phase 2 implementation results
- [ ] Phase 3 implementation results
- [ ] Phase 4 implementation results
- [ ] ROI analysis and metrics
- [ ] Lessons learned and best practices

---

**Document Status:** Living document - updated as project progresses  
**Next Review:** After Phase 2 completion  
**Contact:** Lewis Kimaru
