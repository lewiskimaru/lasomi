# Tutorial: Scalable Local Extraction of Building Footprints with Python

link: https://medium.com/@manoj.gurdev/extracting-building-footprints-from-google-open-buildings-with-python-a-scalable-approach-for-2f176854d24f

This guide details a Python-based workflow for processing the very large CSV files from Google's Open Buildings dataset on your local machine. This method is ideal when you need to extract building footprints for a specific Area of Interest (AOI) from a downloaded data tile that is too large to open directly in GIS software like QGIS.

This approach prioritizes efficiency and scalability by leveraging powerful data handling and geospatial libraries.

## The Challenge: Processing Multi-Gigabyte CSV Files

Google distributes the Open Buildings dataset in large, compressed CSV files. A single file can be over 3GB and contain millions of rows. Attempting to load such a file into a desktop GIS application often leads to memory errors or extremely slow performance. This workflow bypasses that limitation by processing the data programmatically.

## The Solution: A Python & GeoParquet Pipeline

We will use a Python script to:
1.  Efficiently read the large CSV file.
2.  Convert the raw text-based geometry into a proper geospatial format.
3.  Load a separate file defining your specific Area of Interest (AOI).
4.  Perform a spatial query to "clip" or select only the buildings that fall within your AOI.
5.  Export the filtered data to **GeoParquet**, a highly efficient, modern file format for geospatial data that is much faster and smaller than traditional formats like GeoJSON or Shapefiles.

### Prerequisites: Setting Up Your Environment

You need Python and several key libraries installed. You also need the source data files.

**1. Install Required Libraries:**
Open your terminal or command prompt and run the following command:
```bash
pip install geopandas shapely pandas pyarrow
```

**2. Download Source Data:**
*   **Google Open Buildings CSV:** Download the relevant data tile for your region from the [Open Buildings project website](https://sites.research.google/open-buildings/dataset/).
*   **Area of Interest (AOI) File:** You must have a vector file (e.g., `.geojson`, `.shp`, `.kml`) that contains the boundary of the area you want to extract. For example, a file defining a specific city's administrative boundary.

---

## Step-by-Step Extraction Process

This process follows the logic of the Python script provided in the article.

### Step 1: Create a Python Script

Create a new file named `extract_buildings.py` and open it in a code editor.

### Step 2: Add the Python Code

Copy and paste the following code into your `extract_buildings.py` file. Be sure to update the file paths in the script to point to your actual data.

```python
import pandas as pd
import geopandas as gpd
from shapely import wkt
from pathlib import Path

# --- Step 1: Define the paths to your files ---
# IMPORTANT: Update these paths to match your file locations
csv_path = Path("D:/path/to/your/downloaded_open_buildings_tile.csv")
aoi_path = Path("D:/path/to/your/area_of_interest.geojson")
output_path = Path("extracted_buildings_for_aoi.parquet")

# --- Step 2: Read the Google Open Buildings CSV ---
print("🔍 Loading large CSV file... (This may take a moment)")
df = pd.read_csv(csv_path)

# Convert the geometry column (which is in WKT string format) to actual geometry objects
print("📐 Parsing geometries...")
df["geometry"] = df["geometry"].apply(wkt.loads)

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
print(f"✅ Loaded {len(gdf):,} total buildings from CSV.")

# --- Step 3: Load your Area of Interest (AOI) Boundary ---
print("🗺️ Loading AOI boundary...")
aoi = gpd.read_file(aoi_path)

# Ensure the AOI's coordinate system matches the building data
aoi = aoi.to_crs("EPSG:4326")

# Dissolve the AOI into a single polygon for faster filtering
aoi_geom = aoi.geometry.unary_union
print("✅ AOI loaded successfully.")

# --- Step 4: Clip Buildings to the AOI using a spatial query ---
print("✂️  Clipping buildings to AOI...")
# This uses a spatial index for efficient filtering
gdf_aoi = gdf[gdf.intersects(aoi_geom)]
print(f"🎉 Found {len(gdf_aoi):,} buildings within your AOI!")

# --- Step 5: Export the clipped data as a GeoParquet file ---
gdf_aoi.to_parquet(output_path, index=False)
print(f"📦 Successfully exported clipped buildings to: {output_path}")

```

### Step 3: Run the Script

1.  Save the `extract_buildings.py` file after updating the paths.
2.  Open your terminal or command prompt.
3.  Navigate to the directory where you saved the file.
4.  Run the script with the command:
    ```bash
    python extract_buildings.py
    ```

The script will print its progress as it loads, clips, and exports the data.

### Step 4: Visualize the Result in QGIS

1.  Open QGIS.
2.  Go to `Layer` > `Add Layer` > `Add Vector Layer...`.
3.  Browse to your project folder and select the `extracted_buildings_for_aoi.parquet` file.
4.  QGIS will load the GeoParquet file, displaying only the buildings for your specific AOI. You can now style and analyze this data without the performance issues of the original, massive CSV file.