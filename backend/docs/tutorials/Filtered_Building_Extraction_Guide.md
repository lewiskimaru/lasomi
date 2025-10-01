# Tutorial: Extracting High-Confidence Building Footprints from Google's Open Buildings Dataset

link: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons

This guide details how to extract building footprint data from Google's "Open Buildings V3" dataset using the Google Earth Engine (GEE). It focuses specifically on filtering the data to include only buildings with a high confidence score, ensuring a higher quality dataset for analysis.

This process is foundational for developing an automated service that provides reliable building data.

## Objective

To select and export building polygons from a user-defined Area of Interest (AOI) that meet a specific quality threshold (confidence score). The final output will be a KML file suitable for use in Google Earth Pro.

## Understanding the Confidence Score

The Google Open Buildings dataset includes a `confidence` attribute for each building polygon. This score, ranging from 0.0 to 1.0, represents the model's certainty that the detected polygon is indeed a building.

*   A **higher score** (e.g., >= 0.75) indicates a high probability that the feature is a building.
*   A **lower score** (e.g., < 0.70) means the model is less certain, and the feature could be something else or an incorrectly drawn shape.

By filtering on this score, we can remove less certain detections and improve the overall quality of our exported data.

## Tools Required

1.  A Google Account with access to [Google Earth Engine](https://code.earthengine.google.com/).
2.  A web browser.
3.  [Google Earth Pro](https://www.google.com/earth/versions/#earth-pro) desktop application.
4.  An online conversion tool: [QuickMapTools GeoJSON to KML](https://quickmaptools.com/geojson-to-kml).

---

## Step-by-Step Extraction Process

### Step 1: Setting Up the Google Earth Engine Script

1.  Navigate to the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2.  Clear any existing code in the script editor.
3.  Copy and paste the following script. This script is designed to find and export only buildings with a confidence score of 75% or higher.

    ```javascript
    // 1. DEFINE THE SOURCE DATASET
    var google_buildings = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons');

    // 2. FILTER THE DATASET BY THE AREA OF INTEREST (AOI)
    // The AOI must be drawn on the map and named 'AOI' in the imports.
    var buildings_in_aoi = google_buildings.filterBounds(AOI);

    // 3. APPLY A CONFIDENCE SCORE FILTER
    // We only want buildings where the model was at least 75% confident.
    // You can adjust this value (e.g., to 0.7) depending on your needs.
    var high_confidence_buildings = buildings_in_aoi.filter('confidence >= 0.75');

    // 4. VISUALIZE THE FILTERED DATA ON THE MAP
    // This will only show the high-confidence buildings in your AOI.
    Map.addLayer(high_confidence_buildings, {color: '00FF00'}, 'High Confidence Buildings (>= 0.75)');

    // 5. CENTER THE MAP ON THE AOI FOR BETTER VIEWING
    Map.centerObject(AOI, 16);

    // 6. PREPARE THE DATA FOR EXPORT
    Export.table.toDrive({
      collection: high_confidence_buildings,
      description: 'high_confidence_buildings_export',
      folder: 'GEE_Exports',
      fileFormat: 'GeoJSON'
    });
    ```

### Step 2: Defining the Area of Interest (AOI)

1.  On the map interface, find the location you wish to extract data from.
2.  Using the geometry tools above the map, select the **rectangle tool** and draw a box over your target area.
3.  A new import named `geometry` will appear at the top of your script. **This is a critical step:** Click on the name `geometry` and rename it to `AOI` so the script can correctly identify it.

### Step 3: Running the Script and Exporting the Data

1.  Click the **"Run"** button above the script editor.
2.  The map will center on your AOI, and only the high-confidence buildings within it will be displayed (in green).
3.  Select the **"Tasks"** tab on the right-hand panel. A new task named `high_confidence_buildings_export` will appear.
4.  Click the **"RUN"** button next to this task.
5.  A configuration pop-up will appear. The settings are pre-filled by the script. Click the final **"RUN"** button to begin the export.
6.  Once the task is complete, a `high_confidence_buildings_export.geojson` file will be saved to the `GEE_Exports` folder in your Google Drive.

### Step 4: Converting GeoJSON to KML

1.  Download the exported `.geojson` file from your Google Drive.
2.  Go to the [QuickMapTools GeoJSON to KML converter](https://quickmaptools.com/geojson-to-kml).
3.  Upload your `.geojson` file.
4.  Download the resulting `.kml` or `.kmz` file.

### Step 5: Importing into Google Earth Pro

1.  Open the Google Earth Pro desktop application.
2.  Navigate to `File` > `Open...` and select the `.kml` file you just downloaded.
3.  The high-confidence building footprints will now be visible as a layer in Google Earth Pro, ready for further analysis or integration into your projects.