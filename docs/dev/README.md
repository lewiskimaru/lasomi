# Atlas React Frontend Development Guide

## Overview

This guide will help you build a modern React frontend for the Atlas GIS API, replacing the current vanilla JavaScript interface with a more maintainable and scalable solution.

## Current System Analysis

### What We're Replacing
The current web interface (`src/web/templates/`) provides:
- Interactive map interface using Leaflet
- Area of Interest (AOI) drawing tools
- Design file upload functionality  
- Multi-source geospatial data extraction
- Results visualization with layer controls
- Export functionality (KMZ, GeoJSON, CSV, etc.)
- Settings configuration for data sources and processing

### Core Features to Implement

#### 1. **Interactive Map Interface**
- **Map Provider**: Leaflet with React-Leaflet wrapper
- **Drawing Tools**: Polygon, rectangle, and marker drawing
- **Map Sources**: Street, satellite, and terrain views
- **Layer Management**: Toggle visibility of different data layers
- **Zoom Controls**: Custom zoom in/out controls

#### 2. **Area of Interest (AOI) Management**
- **Visual Drawing**: Click-to-draw polygon/rectangle areas
- **Coordinate Display**: Show bounding box coordinates
- **Area Calculation**: Display area in km² or acres
- **Clear/Reset**: Remove drawn areas

#### 3. **Design File Upload**
- **Supported Formats**: GeoJSON, KML, KMZ files
- **File Validation**: Client-side format checking
- **Auto-Navigation**: Zoom to uploaded design extent
- **Layer Visualization**: Display design layers on map

#### 4. **Data Source Configuration**
- **Multi-Source Selection**: 
  - Microsoft Buildings
  - Google Buildings  
  - OSM Buildings, Roads, Railways, Landmarks, Natural features
- **Processing Options**: Filtering, cleaning, simplification settings
- **Export Format**: KMZ, GeoJSON, CSV selection

#### 5. **Results Management**
- **Real-time Processing**: WebSocket or polling for job status
- **Layer Controls**: Toggle visibility of result layers
- **Data Visualization**: Styled rendering of extracted features
- **Export Downloads**: Generate and download result files

#### 6. **User Interface Components**
- **Responsive Sidebar**: Collapsible panel for controls
- **Modal Dialogs**: Settings, export, and upload workflows
- **Toast Notifications**: Success/error feedback
- **Loading States**: Progress indicators for API calls

## Technology Stack Recommendations

### Core Dependencies
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.1.0",
  "@types/react": "^18.2.0",
  "@types/react-dom": "^18.2.0"
}
```

### UI & Styling
```json
{
  "tailwindcss": "^3.3.0",
  "@headlessui/react": "^1.7.0",
  "@heroicons/react": "^2.0.0",
  "react-hot-toast": "^2.4.0"
}
```

### Map & Geospatial
```json
{
  "react-leaflet": "^4.2.0",
  "leaflet": "^1.9.4",
  "leaflet-draw": "^1.0.4",
  "@types/leaflet": "^1.9.0"
}
```

### State Management & API
```json
{
  "zustand": "^4.4.0",
  "react-query": "^3.39.0",
  "axios": "^1.4.0"
}
```

### File Handling
```json
{
  "react-dropzone": "^14.2.0",
  "file-saver": "^2.0.5"
}
```

### Development Tools
```json
{
  "vite": "^4.4.0",
  "@vitejs/plugin-react": "^4.0.0",
  "eslint": "^8.45.0",
  "prettier": "^3.0.0"
}
```

## Project Structure

```
atlas-react-frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # Basic UI elements
│   │   ├── map/             # Map-related components
│   │   ├── forms/           # Form components
│   │   └── layout/          # Layout components
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx    # Main map interface
│   │   ├── Documentation.tsx
│   │   └── Developer.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useAtlasAPI.ts
│   │   ├── useMap.ts
│   │   └── useFileUpload.ts
│   ├── services/            # API services
│   │   ├── atlasAPI.ts
│   │   ├── mapServices.ts
│   │   └── fileServices.ts
│   ├── stores/              # Zustand stores
│   │   ├── mapStore.ts
│   │   ├── dataStore.ts
│   │   └── uiStore.ts
│   ├── types/               # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── map.ts
│   │   └── components.ts
│   ├── utils/               # Utility functions
│   │   ├── geometry.ts
│   │   ├── formatting.ts
│   │   └── validation.ts
│   ├── styles/              # Global styles
│   │   ├── globals.css
│   │   └── components.css
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

## Quick Start Commands

### 1. Initialize Project
```bash
# Create React app with Vite
npm create vite@latest atlas-react-frontend -- --template react-ts
cd atlas-react-frontend

# Install dependencies
npm install

# Install additional packages
npm install react-leaflet leaflet leaflet-draw @types/leaflet
npm install tailwindcss @headlessui/react @heroicons/react
npm install zustand react-query axios
npm install react-dropzone file-saver
npm install react-hot-toast
```

### 2. Setup Tailwind CSS
```bash
# Initialize Tailwind
npx tailwindcss init -p

# Update tailwind.config.js content paths
# Add to src/styles/globals.css:
# @tailwind base;
# @tailwind components;  
# @tailwind utilities;
```

### 3. Development Server
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Key Implementation Considerations

### 1. **State Management Strategy**
- **Zustand** for global state (map state, API data, UI state)
- **React Query** for server state management and caching
- **Local component state** for form inputs and temporary UI state

### 2. **Map Implementation Approach**
- Use **React-Leaflet** as the primary map component
- Create custom hooks for map interactions
- Implement drawing tools with **leaflet-draw**
- Handle map state in Zustand store

### 3. **API Integration Pattern**
- Create typed API service functions
- Use React Query for data fetching and caching
- Implement error handling and retry logic
- Handle file uploads with progress tracking

### 4. **Component Design Principles**
- **Composition over inheritance**
- **Single responsibility principle**
- **Reusable and configurable components**
- **Proper TypeScript typing**

### 5. **Performance Considerations**
- **Lazy loading** for route components
- **Memoization** for expensive computations
- **Virtual scrolling** for large datasets
- **Debounced API calls** for search/input

### 6. **Accessibility Requirements**
- **ARIA labels** for interactive elements
- **Keyboard navigation** support
- **Screen reader** compatibility
- **Color contrast** compliance

## Next Steps

1. **Read the Component Architecture Guide** (`component-architecture.md`)
2. **Review the API Integration Guide** (`api-integration.md`)
3. **Study the Styling Guide** (`styling-guide.md`)
4. **Follow the Implementation Roadmap** (`implementation-roadmap.md`)

## Development Timeline Estimate

- **Setup & Basic Structure**: 1-2 days
- **Map Component Implementation**: 3-4 days  
- **API Integration**: 2-3 days
- **UI Components & Styling**: 4-5 days
- **File Upload & Export**: 2-3 days
- **Testing & Polish**: 2-3 days

**Total Estimated Time**: 14-20 days for a junior developer

## Support & Resources

- **Current Web Interface**: `/src/web/templates/index.html` (reference implementation)
- **API Documentation**: `/docs` endpoint (Swagger UI)
- **Atlas API**: Base URL `/api/v2/`
- **Design System**: Current CSS variables in `/src/web/static/css/atlas.css`

This guide provides the foundation for building a professional React frontend. The following detailed guides will walk you through each aspect of the implementation.
