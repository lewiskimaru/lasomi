# Tutorial: Extracting Google & Microsoft Building Footprints via Google Earth Engine

link: https://www.geodose.com/2023/08/how-to-download-google-microsoft-building-data.html

This document outlines the manual process for extracting building footprint data for a specific Area of Interest (AOI) using the Google Earth Engine (GEE) platform. The final output is a KML/KMZ file ready for use in Google Earth Pro.

This guide serves as the foundational logic for developing a FastAPI service to automate this workflow.

## Objective

To download building footprint polygons from both Google's and Microsoft's open datasets, export them as GeoJSON files, and convert them for use in Google Earth Pro.

## Tools Required

1.  A Google Account with access to [Google Earth Engine](https://code.earthengine.google.com/).
2.  A web browser.
3.  [Google Earth Pro](https://www.google.com/earth/versions/#earth-pro) desktop application.
4.  An online conversion tool: [QuickMapTools GeoJSON to KML](https://quickmaptools.com/geojson-to-kml).

---

## Step-by-Step Extraction Process

### Step 1: Setting Up the Google Earth Engine Script

1.  Navigate to the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2.  In the central script editor panel, delete any default code.
3.  Copy and paste the following script. This example is configured to extract data for Kenya.

    ```javascript
    //MICROSOFT BUILDING FOLDER. CHECK IT FOR A SPECIFIC COUNTRY
    var ee_folder = ee.data.listAssets("projects/sat-io/open-datasets/MSBuildings");
    print(ee_folder);

    //BUILDING FEATURE COLLECTION FOR MICROSOFT AND GOOGLE
    var kenya_ms = ee.FeatureCollection('projects/sat-io/open-datasets/MSBuildings/Kenya');
    var google_building = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons');

    //CLIP BUILDING WITH AOI
    var ms_clip = kenya_ms.filterBounds(AOI);
    var google_clip = google_building.filterBounds(AOI);

    //ADD BUILDING TO THE MAP
    Map.addLayer(ms_clip, {color: 'blue'}, 'Microsoft Buildings Kenya');
    Map.addLayer(google_clip, {color: 'yellow'}, 'Google Buildings Kenya');

    //SET MAP CENTER
    Map.setCenter(36.8219, -1.2921, 10); // Coordinates for Nairobi, zoom level 10

    //EXPORT GOOGLE DATA TO GOOGLE DRIVE IN GEOJSON FORMAT
    Export.table.toDrive({
      collection: google_clip,
      description: 'google_clip_kenya', // Changed description for clarity
      folder: 'GEE_Exports',
      fileFormat:'GeoJSON',
    });

    //EXPORT MICROSOFT DATA TO GOOGLE DRIVE IN GEOJSON FORMAT
    Export.table.toDrive({
      collection: ms_clip,
      description: 'ms_clip_kenya', // Changed description for clarity
      folder: 'GEE_Exports',
      fileFormat:'GeoJSON',
    });
    ```

    **Note:** I have added an export task for the Microsoft data as well so you can get both files. I also made the `description` and `folder` names more specific.

### Step 2: Defining the Area of Interest (AOI)

1.  On the interactive map, navigate to your desired location within Kenya.
2.  Use the geometry tools located above the map window. Click the **rectangle icon**.
3.  Draw a rectangle over your target area. A new item named `geometry` will appear in the "Imports" section at the top of your script.
4.  **This is a critical step:** Click on the variable name `geometry` and rename it to `AOI`. The script requires this specific name to function correctly.

### Step 3: Running the Script and Exporting the Data

1.  Click the **"Run"** button located above the script editor. The map will center on Nairobi, and the building footprints within your drawn AOI will be highlighted in blue (Microsoft) and yellow (Google).
2.  Switch to the **"Tasks"** tab on the right-hand panel.
3.  Two new tasks, `google_clip_kenya` and `ms_clip_kenya`, will be listed under "Unsubmitted tasks".
4.  Click the **"RUN"** button next to each task.
5.  A configuration window will pop up for each. The details are pre-filled by the script. Simply click the final **"RUN"** button in the pop-up.
6.  The tasks will begin processing. Once complete, the `google_clip_kenya.geojson` and `ms_clip_kenya.geojson` files will be available in your Google Drive, inside a folder named `GEE_Exports`.

### Step 4: Converting GeoJSON to KML

1.  Download the exported `.geojson` files from your Google Drive to your local machine.
2.  Open your web browser and navigate to [https://quickmaptools.com/geojson-to-kml](https://quickmaptools.com/geojson-to-kml).
3.  Upload your `.geojson` file to the website.
4.  The tool will process the file and provide a download link for the converted `.kml` or `.kmz` file. Download this new file.

### Step 5: Importing into Google Earth Pro

1.  Open the Google Earth Pro desktop application.
2.  Go to `File` > `Open...`.
3.  Navigate to and select the `.kml` or `.kmz` file you downloaded from the conversion tool.
4.  The building footprints will now be loaded as a layer in Google Earth Pro, allowing for further visualization, analysis, and integration with other datasets.
