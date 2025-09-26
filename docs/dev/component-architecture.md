# Component Architecture Guide

## Overview

This guide details the React component structure for the Atlas frontend, providing clear patterns and examples for building maintainable, reusable components.

## Architecture Principles

### 1. **Component Hierarchy**
```
App
├── Layout
│   ├── TopBar
│   ├── Sidebar
│   └── MainContent
├── Pages
│   ├── Dashboard (Main Map Interface)
│   ├── Documentation
│   └── Developer
└── Providers
    ├── QueryProvider
    ├── ToastProvider
    └── ThemeProvider
```

### 2. **Component Categories**

#### **Layout Components** (`src/components/layout/`)
- **TopBar**: Navigation, search, map type selector
- **Sidebar**: Main navigation, collapsible
- **MainContent**: Content wrapper with responsive design
- **PageLayout**: Common page structure for docs/developer pages

#### **Map Components** (`src/components/map/`)
- **MapContainer**: Main map wrapper with Leaflet integration
- **DrawingControls**: Polygon, rectangle, marker drawing tools
- **LayerControls**: Toggle visibility of data layers
- **ZoomControls**: Custom zoom in/out buttons
- **MapTypeSelector**: Switch between street/satellite/terrain

#### **UI Components** (`src/components/ui/`)
- **Button**: Various button styles and states
- **Modal**: Reusable modal dialog
- **Card**: Content card wrapper
- **Form**: Form inputs, validation
- **Toast**: Notification system
- **LoadingSpinner**: Loading indicators
- **Accordion**: Collapsible content sections

#### **Feature Components** (`src/components/features/`)
- **AOIPanel**: Area of Interest management
- **DesignUpload**: File upload and processing
- **ResultsPanel**: Display extraction results
- **SettingsModal**: Configuration options
- **ExportModal**: Export format selection

## Detailed Component Specifications

### 1. Layout Components

#### TopBar Component
```typescript
// src/components/layout/TopBar.tsx
interface TopBarProps {
  onSearch: (query: string) => void;
  onMapTypeChange: (type: MapType) => void;
  currentMapType: MapType;
}

export const TopBar: React.FC<TopBarProps> = ({
  onSearch,
  onMapTypeChange,
  currentMapType
}) => {
  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <Logo />
      </div>
      <div className="top-bar-center">
        <SearchInput onSearch={onSearch} />
      </div>
      <div className="top-bar-right">
        <MapTypeSelector 
          value={currentMapType}
          onChange={onMapTypeChange}
        />
      </div>
    </div>
  );
};
```

#### Sidebar Component
```typescript
// src/components/layout/Sidebar.tsx
interface SidebarItem {
  id: string;
  label: string;
  icon: React.ComponentType;
  href: string;
  active?: boolean;
}

interface SidebarProps {
  items: SidebarItem[];
  collapsed?: boolean;
  onToggle?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  items,
  collapsed = false,
  onToggle
}) => {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <nav className="sidebar-nav">
        {items.map(item => (
          <SidebarNavItem key={item.id} {...item} />
        ))}
      </nav>
    </aside>
  );
};
```

### 2. Map Components

#### MapContainer Component
```typescript
// src/components/map/MapContainer.tsx
import { MapContainer as LeafletMapContainer, TileLayer } from 'react-leaflet';
import { useMapStore } from '@/stores/mapStore';

interface MapContainerProps {
  className?: string;
  children?: React.ReactNode;
}

export const MapContainer: React.FC<MapContainerProps> = ({
  className = '',
  children
}) => {
  const { center, zoom, mapType } = useMapStore();
  
  return (
    <div className={`map-wrapper ${className}`}>
      <LeafletMapContainer
        center={center}
        zoom={zoom}
        className="map-container"
        zoomControl={false}
      >
        <TileLayer
          url={getMapTileUrl(mapType)}
          attribution={getMapAttribution(mapType)}
        />
        {children}
      </LeafletMapContainer>
      
      {/* Overlay Controls */}
      <ZoomControls />
      <DrawingControls />
      <LayerCyclingControl />
    </div>
  );
};
```

#### DrawingControls Component
```typescript
// src/components/map/DrawingControls.tsx
interface DrawingControlsProps {
  onShapeStart: (type: ShapeType) => void;
  onShapeComplete: (shape: DrawnShape) => void;
  onDelete: () => void;
  activeDrawing?: ShapeType;
}

export const DrawingControls: React.FC<DrawingControlsProps> = ({
  onShapeStart,
  onShapeComplete,
  onDelete,
  activeDrawing
}) => {
  return (
    <div className="drawing-controls">
      <DrawingButton
        type="marker"
        active={activeDrawing === 'marker'}
        onClick={() => onShapeStart('marker')}
        icon={PencilIcon}
        tooltip="Drawing Mode"
      />
      <DrawingButton
        type="polygon"
        active={activeDrawing === 'polygon'}
        onClick={() => onShapeStart('polygon')}
        icon={PolygonIcon}
        tooltip="Draw Polygon"
      />
      <DrawingButton
        type="rectangle"
        active={activeDrawing === 'rectangle'}
        onClick={() => onShapeStart('rectangle')}
        icon={SquareIcon}
        tooltip="Draw Rectangle"
      />
      <DrawingButton
        type="delete"
        onClick={onDelete}
        icon={TrashIcon}
        tooltip="Delete Shape"
        variant="danger"
      />
    </div>
  );
};
```

### 3. Feature Components

#### AOIPanel Component
```typescript
// src/components/features/AOIPanel.tsx
interface AOIPanelProps {
  aoi: AOIData | null;
  onClear: () => void;
  onRun: () => void;
  isProcessing: boolean;
}

export const AOIPanel: React.FC<AOIPanelProps> = ({
  aoi,
  onClear,
  onRun,
  isProcessing
}) => {
  return (
    <Card className="aoi-panel">
      <CardHeader>
        <h3>Area of Interest</h3>
        <SettingsButton />
      </CardHeader>
      
      <CardBody>
        <DesignUploadAccordion />
        
        <AOIAccordion aoi={aoi} />
        
        <div className="aoi-actions">
          <Button variant="ghost" onClick={onClear}>
            Clear
          </Button>
          <Button 
            variant="primary" 
            onClick={onRun}
            disabled={!aoi || isProcessing}
            loading={isProcessing}
          >
            <PlayIcon className="w-4 h-4" />
            Run
          </Button>
        </div>
      </CardBody>
    </Card>
  );
};
```

#### DesignUpload Component
```typescript
// src/components/features/DesignUpload.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface DesignUploadProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
  uploadedDesign: DesignData | null;
}

export const DesignUpload: React.FC<DesignUploadProps> = ({
  onUpload,
  isUploading,
  uploadedDesign
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.geojson', '.json'],
      'application/vnd.google-earth.kml+xml': ['.kml'],
      'application/vnd.google-earth.kmz': ['.kmz']
    },
    multiple: false
  });

  return (
    <div className="design-upload">
      {uploadedDesign ? (
        <DesignInfo design={uploadedDesign} />
      ) : (
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          <UploadIcon className="w-6 h-6" />
          <p>Upload Design File</p>
          <small>GeoJSON, KML, or KMZ</small>
        </div>
      )}
    </div>
  );
};
```

### 4. UI Components

#### Modal Component
```typescript
// src/components/ui/Modal.tsx
import { Dialog, Transition } from '@headlessui/react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md'
}) => {
  return (
    <Transition show={isOpen} as={React.Fragment}>
      <Dialog onClose={onClose} className="modal-overlay">
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="modal-backdrop" />
        </Transition.Child>

        <div className="modal-container">
          <Transition.Child
            as={React.Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Dialog.Panel className={`modal-panel modal-${size}`}>
              <div className="modal-header">
                <Dialog.Title className="modal-title">
                  {title}
                </Dialog.Title>
                <button onClick={onClose} className="modal-close">
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>
              
              <div className="modal-body">
                {children}
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
};
```

#### Button Component
```typescript
// src/components/ui/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon: Icon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const isDisabled = disabled || loading;

  return (
    <button
      className={`btn btn-${variant} btn-${size} ${className}`}
      disabled={isDisabled}
      {...props}
    >
      {loading && <LoadingSpinner className="w-4 h-4" />}
      {Icon && !loading && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
};
```

## Component Patterns

### 1. **Custom Hooks Pattern**
```typescript
// src/hooks/useMapInteraction.ts
export const useMapInteraction = () => {
  const { setAOI, clearAOI } = useMapStore();
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingType, setDrawingType] = useState<ShapeType | null>(null);

  const startDrawing = useCallback((type: ShapeType) => {
    setIsDrawing(true);
    setDrawingType(type);
  }, []);

  const completeDrawing = useCallback((shape: DrawnShape) => {
    setAOI(shape);
    setIsDrawing(false);
    setDrawingType(null);
  }, [setAOI]);

  return {
    isDrawing,
    drawingType,
    startDrawing,
    completeDrawing,
    clearAOI
  };
};
```

### 2. **Compound Component Pattern**
```typescript
// src/components/ui/Card.tsx
export const Card = ({ children, className = '' }) => (
  <div className={`card ${className}`}>
    {children}
  </div>
);

Card.Header = ({ children, className = '' }) => (
  <div className={`card-header ${className}`}>
    {children}
  </div>
);

Card.Body = ({ children, className = '' }) => (
  <div className={`card-body ${className}`}>
    {children}
  </div>
);

Card.Footer = ({ children, className = '' }) => (
  <div className={`card-footer ${className}`}>
    {children}
  </div>
);

// Usage:
<Card>
  <Card.Header>
    <h3>Title</h3>
  </Card.Header>
  <Card.Body>
    Content here
  </Card.Body>
</Card>
```

### 3. **Render Props Pattern**
```typescript
// src/components/features/DataFetcher.tsx
interface DataFetcherProps<T> {
  url: string;
  children: (data: {
    data: T | null;
    loading: boolean;
    error: Error | null;
    refetch: () => void;
  }) => React.ReactNode;
}

export function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const { data, isLoading: loading, error, refetch } = useQuery<T>(url);
  
  return <>{children({ data: data ?? null, loading, error, refetch })}</>;
}

// Usage:
<DataFetcher<DataSource[]> url="/api/v2/data-sources">
  {({ data, loading, error }) => (
    loading ? <LoadingSpinner /> : 
    error ? <ErrorMessage error={error} /> :
    <DataSourceList sources={data} />
  )}
</DataFetcher>
```

## Testing Strategy

### 1. **Component Testing**
```typescript
// src/components/ui/__tests__/Button.test.tsx
import { render, fireEvent, screen } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### 2. **Integration Testing**
```typescript
// src/components/features/__tests__/AOIPanel.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AOIPanel } from '../AOIPanel';

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('AOIPanel', () => {
  it('enables run button when AOI is set', () => {
    const mockAOI = { /* mock AOI data */ };
    
    renderWithProviders(
      <AOIPanel 
        aoi={mockAOI}
        onRun={jest.fn()}
        onClear={jest.fn()}
        isProcessing={false}
      />
    );
    
    expect(screen.getByText('Run')).not.toBeDisabled();
  });
});
```

## Performance Optimizations

### 1. **Memoization**
```typescript
// src/components/map/LayerControls.tsx
export const LayerControls = React.memo(({ layers, onToggle }) => {
  const memoizedLayers = useMemo(() => 
    layers.filter(layer => layer.visible), 
    [layers]
  );

  return (
    <div className="layer-controls">
      {memoizedLayers.map(layer => (
        <LayerToggle 
          key={layer.id}
          layer={layer}
          onToggle={onToggle}
        />
      ))}
    </div>
  );
});
```

### 2. **Lazy Loading**
```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Documentation = lazy(() => import('./pages/Documentation'));
const Developer = lazy(() => import('./pages/Developer'));

export const App = () => (
  <Router>
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/docs" element={<Documentation />} />
        <Route path="/developer" element={<Developer />} />
      </Routes>
    </Suspense>
  </Router>
);
```

## Next Steps

1. **Review API Integration Guide** (`api-integration.md`)
2. **Study Styling Guide** (`styling-guide.md`)
3. **Implement components following these patterns**
4. **Set up testing infrastructure**
5. **Create component storybook for documentation**

This architecture provides a solid foundation for building scalable, maintainable React components that match the functionality of the current Atlas web interface.
