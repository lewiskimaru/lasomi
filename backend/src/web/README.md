# Atlas Web Interface

This directory contains the web interface for the Atlas Geospatial API.

## Structure

```
web/
├── routes.py           # FastAPI routes for web interface
├── templates/          # Jinja2 HTML templates
│   ├── index.html     # Main web interface
│   └── docs.html      # Documentation page
└── static/            # Static assets
    ├── css/
    │   └── atlas.css  # Main stylesheet
    └── js/
        └── atlas.js   # Main JavaScript functionality
```

## Features

### Main Interface (`/web/`)
- **Interactive Map**: Leaflet-based map with drawing tools
- **Data Source Selection**: Toggle between Microsoft Buildings, Google Buildings, and OSM data
- **AOI Definition**: Draw polygons, upload GeoJSON, or search by coordinates
- **Processing Options**: Configure filters and export preferences
- **Real-time Results**: Visualize extracted features with layer controls
- **Multi-format Export**: Download results in GeoJSON, KML, CSV, DWG, or Shapefile

### Map Controls
- **Map Types**: Streets, Satellite, Terrain, Dark themes
- **Drawing Tools**: Polygon drawing with Leaflet.draw
- **Search**: Location search and coordinate-based navigation
- **Zoom Controls**: Custom zoom in/out buttons
- **Layer Panel**: Toggle result layers on/off

### Export Modal
- **Format Selection**: Visual format picker with descriptions
- **Source Selection**: Choose specific data sources to include
- **Metadata Options**: Include/exclude processing metadata
- **Progress Tracking**: Real-time export progress with auto-download

## Technologies Used

- **Frontend**: HTML5, CSS3 (Grid/Flexbox), Vanilla JavaScript
- **Mapping**: Leaflet.js with Leaflet.draw plugin
- **Icons**: Font Awesome 6
- **Animations**: CSS animations with animate.css
- **Backend**: FastAPI with Jinja2 templates
- **Styling**: CSS custom properties (variables) for theming

## Browser Support

- Modern browsers (Chrome 88+, Firefox 85+, Safari 14+, Edge 88+)
- Mobile responsive design
- Progressive enhancement for older browsers

## Usage

1. Start the FastAPI server
2. Navigate to `http://localhost:8000/web/`
3. Draw your area of interest on the map
4. Select data sources and configure options
5. Extract features and visualize results
6. Export data in your preferred format

## Development

The interface is built with modern web standards and follows progressive enhancement principles. It can work offline for basic map viewing once loaded.

### Key JavaScript Classes

- `AtlasInterface`: Main application controller
- Event-driven architecture with proper error handling
- Async/await for API communication
- ES6+ features with fallbacks