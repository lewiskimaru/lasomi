# Map Tile Sources for Personal Mapping Service

This document provides a collection of tile server URLs for building a flexible mapping service where users can choose their preferred map source for different layer types (street, satellite, terrain, hybrid).

## Important Notes

⚠️ **For Personal Use Only**: This service is designed for personal/development use to avoid API management complexity. Some tile sources may have usage restrictions for commercial applications.

⚠️ **Attribution Required**: Always include proper attribution when using these tile sources.

⚠️ **Rate Limiting**: Some services may implement rate limiting. For production use, consider official APIs.

## Available Tile Sources

### Street Map Sources

#### OpenStreetMap (Recommended)
```
https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
Attribution: © OpenStreetMap contributors
```

#### Google Roadmap
```
https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}
Attribution: © Google
```

#### CartoDB Positron (Light Theme)
```
https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png
Attribution: © OpenStreetMap contributors, © CartoDB
```

#### CartoDB Dark Matter (Dark Theme)
```
https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png
Attribution: © OpenStreetMap contributors, © CartoDB
```

### Satellite/Aerial Sources

#### Esri World Imagery (Recommended)
```
https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
Attribution: © Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community
```

#### Google Satellite
```
https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}
Attribution: © Google
```

#### Bing Aerial (Requires Quadkey conversion)
```
https://ecn.t{subdomain}.tiles.virtualearth.net/tiles/a{quadkey}.jpeg?g=1
Attribution: © Microsoft Corporation
Note: Requires quadkey conversion from x/y/z coordinates
```

### Hybrid Sources (Satellite + Labels)

#### Google Hybrid (Recommended)
```
https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}
Attribution: © Google
```

#### Esri World Imagery with Labels
```
https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
+ https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}
Attribution: © Esri
Note: Requires layering two tile sources
```

### Terrain Sources

#### OpenTopoMap (Recommended)
```
https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png
Attribution: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)
```

#### Google Terrain
```
https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}
Attribution: © Google
```

#### Stamen Terrain
```
https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg
Attribution: Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL
```

#### USGS Topo
```
https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}
Attribution: USGS
Note: US-focused coverage
```

## Frontend Implementation Example

```javascript
const mapSources = {
    street: {
        osm: {
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution: '© OpenStreetMap contributors'
        },
        google: {
            url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attribution: '© Google'
        },
        carto_light: {
            url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attribution: '© OpenStreetMap contributors, © CartoDB'
        }
    },
    satellite: {
        esri: {
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attribution: '© Esri'
        },
        google: {
            url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attribution: '© Google'
        }
    },
    hybrid: {
        google: {
            url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attribution: '© Google'
        }
    },
    terrain: {
        opentopo: {
            url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            attribution: '© OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap'
        },
        google: {
            url: 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}',
            attribution: '© Google'
        },
        stamen: {
            url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
            attribution: 'Map tiles by Stamen Design, Data by OpenStreetMap'
        }
    }
};

// User selection interface
function createLayerSelector(layerType) {
    const sources = mapSources[layerType];
    // Create dropdown/radio buttons for user to select preferred source
    // Return selected source configuration
}
```

## URL Template Variables

- `{z}` - Zoom level (0-18+ depending on source)
- `{x}` - Tile X coordinate
- `{y}` - Tile Y coordinate  
- `{s}` - Subdomain (usually a, b, c for load balancing)
- `{r}` - Retina/high-DPI indicator (@2x)
- `{subdomain}` - Numeric subdomain (0-3 for Bing)
- `{quadkey}` - Bing's quadkey system (requires conversion)

## Recommended Combinations

**For General Use:**
- Street: OpenStreetMap
- Satellite: Esri World Imagery or Google Hybrid (with labels)
- Terrain: OpenTopoMap

**For Dark Theme Applications:**
- Street: CartoDB Dark Matter
- Satellite: Esri World Imagery
- Terrain: OpenTopoMap

## Legal Considerations

While these sources work for personal development, always check the terms of service for your specific use case. For production applications with significant traffic, consider:

- Official Google Maps API
- Mapbox
- OpenStreetMap with commercial hosting
- Esri ArcGIS API

## Server-Side Proxy (Optional)

For additional control and to avoid CORS issues, consider implementing a server-side tile proxy:

```javascript
// Express.js example
app.get('/tiles/:source/:z/:x/:y', (req, res) => {
    const { source, z, x, y } = req.params;
    const tileUrl = buildTileUrl(source, z, x, y);
    // Fetch and proxy the tile
});
```

This approach allows you to:
- Add caching
- Implement usage logging
- Handle authentication if needed
- Normalize different tile URL formats