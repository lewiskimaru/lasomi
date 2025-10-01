# Styling and Design System Guide

## Overview

This guide provides comprehensive documentation for implementing the Atlas design system in React, maintaining visual consistency with the current interface while leveraging modern CSS-in-JS or Tailwind CSS approaches.

## Design System Overview

### Current Color Palette
The existing Atlas interface uses a professional dark theme with the following color scheme:

```css
/* From the current atlas.css */
:root {
  /* Core Colors */
  --page-background: #062226;      /* Deep dark blue-green */
  --sidebar-background: #132f35;   /* Darker blue-green */
  --card-background: #132f35;      /* Same as sidebar */
  --primary-color: #0e5a81;        /* Medium blue */
  --secondary-color: #1f3539;      /* Dark blue-green */
  
  /* Text Colors */
  --text-primary: #ffffff;         /* Pure white */
  --text-secondary: #b0c4c8;       /* Light blue-gray */
  
  /* UI Colors */
  --border-color: rgba(255, 255, 255, 0.1);
  --success-color: #059669;        /* Green */
  --warning-color: #d97706;        /* Orange */
  --danger-color: #dc2626;         /* Red */
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.2);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3);
}
```

## Tailwind CSS Configuration

### 1. Tailwind Config Setup
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        // Atlas brand colors
        atlas: {
          page: '#062226',
          sidebar: '#132f35',
          card: '#132f35',
          primary: '#0e5a81',
          secondary: '#1f3539',
        },
        // Text colors
        text: {
          primary: '#ffffff',
          secondary: '#b0c4c8',
        },
        // Semantic colors
        success: '#059669',
        warning: '#d97706',
        danger: '#dc2626',
        // Border colors
        border: {
          DEFAULT: 'rgba(255, 255, 255, 0.1)',
          light: 'rgba(255, 255, 255, 0.05)',
          medium: 'rgba(255, 255, 255, 0.15)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'card': '5px',
      },
      boxShadow: {
        'atlas-sm': '0 1px 2px 0 rgb(0 0 0 / 0.2)',
        'atlas-md': '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2)',
        'atlas-lg': '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.15s ease-in-out',
        'slide-in': 'slideIn 0.25s ease-in-out',
        'spin-slow': 'spin 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@headlessui/tailwindcss'),
    require('@tailwindcss/forms'),
  ],
};
```

### 2. Global Styles
```css
/* src/styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@layer base {
  * {
    @apply border-border;
  }
  
  body {
    @apply bg-atlas-page text-text-primary font-sans;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
  
  /* Scrollbar styling */
  ::-webkit-scrollbar {
    @apply w-2;
  }
  
  ::-webkit-scrollbar-track {
    @apply bg-atlas-sidebar;
  }
  
  ::-webkit-scrollbar-thumb {
    @apply bg-border rounded-full;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    @apply bg-border-medium;
  }
}

@layer components {
  /* Button variants */
  .btn {
    @apply inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none;
  }
  
  .btn-primary {
    @apply bg-atlas-primary text-white hover:bg-blue-600 focus:ring-atlas-primary;
  }
  
  .btn-secondary {
    @apply bg-atlas-secondary text-text-primary hover:bg-opacity-80 focus:ring-atlas-secondary;
  }
  
  .btn-ghost {
    @apply bg-transparent text-text-secondary hover:bg-atlas-secondary hover:text-text-primary focus:ring-atlas-secondary;
  }
  
  .btn-danger {
    @apply bg-danger text-white hover:bg-red-700 focus:ring-danger;
  }
  
  .btn-success {
    @apply bg-success text-white hover:bg-green-700 focus:ring-success;
  }
  
  /* Card components */
  .card {
    @apply bg-atlas-card border border-border rounded-card shadow-atlas-md;
  }
  
  .card-header {
    @apply flex items-center justify-between p-4 border-b border-border;
  }
  
  .card-body {
    @apply p-4;
  }
  
  .card-footer {
    @apply px-4 py-3 border-t border-border bg-atlas-sidebar rounded-b-card;
  }
  
  /* Form elements */
  .form-input {
    @apply block w-full px-3 py-2 bg-atlas-sidebar border border-border rounded-md text-text-primary placeholder-text-secondary focus:border-atlas-primary focus:ring-1 focus:ring-atlas-primary;
  }
  
  .form-select {
    @apply block w-full px-3 py-2 bg-atlas-sidebar border border-border rounded-md text-text-primary focus:border-atlas-primary focus:ring-1 focus:ring-atlas-primary;
  }
  
  .form-checkbox {
    @apply w-4 h-4 text-atlas-primary bg-atlas-sidebar border border-border rounded focus:ring-atlas-primary focus:ring-2;
  }
  
  .form-radio {
    @apply w-4 h-4 text-atlas-primary bg-atlas-sidebar border border-border focus:ring-atlas-primary focus:ring-2;
  }
  
  /* Layout components */
  .top-bar {
    @apply flex items-center justify-between h-14 px-4 bg-atlas-sidebar border-b border-border;
  }
  
  .sidebar {
    @apply w-16 bg-atlas-sidebar border-r border-border flex flex-col;
  }
  
  .sidebar-nav {
    @apply flex flex-col gap-1 p-2;
  }
  
  .sidebar-nav-item {
    @apply flex items-center justify-center w-12 h-12 text-text-secondary hover:text-text-primary hover:bg-atlas-secondary rounded-md transition-colors;
  }
  
  .sidebar-nav-item.active {
    @apply text-text-primary bg-atlas-primary;
  }
  
  /* Modal components */
  .modal-overlay {
    @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50;
  }
  
  .modal-panel {
    @apply bg-atlas-card border border-border rounded-lg shadow-atlas-lg max-h-[90vh] overflow-y-auto;
  }
  
  .modal-sm {
    @apply w-full max-w-sm;
  }
  
  .modal-md {
    @apply w-full max-w-lg;
  }
  
  .modal-lg {
    @apply w-full max-w-2xl;
  }
  
  .modal-xl {
    @apply w-full max-w-4xl;
  }
}

@layer utilities {
  .text-gradient {
    @apply bg-gradient-to-r from-atlas-primary to-blue-400 bg-clip-text text-transparent;
  }
  
  .glass-effect {
    @apply bg-white bg-opacity-5 backdrop-blur-sm border border-white border-opacity-10;
  }
}
```

## Component Styling Patterns

### 1. Layout Components

#### TopBar Component Styles
```typescript
// src/components/layout/TopBar.tsx
export const TopBar: React.FC<TopBarProps> = ({ onSearch, onMapTypeChange, currentMapType }) => {
  return (
    <div className="top-bar">
      {/* Left section */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-atlas-primary rounded-md flex items-center justify-center">
            <SatelliteIcon className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-semibold text-text-primary">Atlasomi</span>
        </div>
      </div>
      
      {/* Center section */}
      <div className="flex-1 max-w-md mx-4">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            placeholder="Search location..."
            className="form-input pl-10 w-full"
            onChange={(e) => onSearch(e.target.value)}
          />
          <SearchSuggestions />
        </div>
      </div>
      
      {/* Right section */}
      <div className="flex items-center gap-3">
        <select
          value={currentMapType}
          onChange={(e) => onMapTypeChange(e.target.value as MapType)}
          className="form-select"
        >
          <option value="streets">Street</option>
          <option value="satellite">Satellite</option>
          <option value="terrain">Terrain</option>
        </select>
      </div>
    </div>
  );
};
```

#### Sidebar Component Styles
```typescript
// src/components/layout/Sidebar.tsx
export const Sidebar: React.FC<SidebarProps> = ({ items, collapsed = false }) => {
  return (
    <aside className={`sidebar ${collapsed ? 'w-0 overflow-hidden' : 'w-16'} transition-all duration-300`}>
      <nav className="sidebar-nav">
        {items.map((item) => (
          <Link
            key={item.id}
            to={item.href}
            className={`sidebar-nav-item group relative ${item.active ? 'active' : ''}`}
            title={item.label}
          >
            <item.icon className="w-6 h-6" />
            
            {/* Tooltip */}
            <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap">
              {item.label}
            </div>
          </Link>
        ))}
      </nav>
    </aside>
  );
};
```

### 2. Map Components

#### Map Controls Styling
```typescript
// src/components/map/DrawingControls.tsx
export const DrawingControls: React.FC<DrawingControlsProps> = ({ 
  onShapeStart, 
  activeDrawing 
}) => {
  return (
    <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
      <DrawingButton
        active={activeDrawing === 'marker'}
        onClick={() => onShapeStart('marker')}
        tooltip="Drawing Mode"
      >
        <PencilIcon className="w-5 h-5" />
      </DrawingButton>
      
      <DrawingButton
        active={activeDrawing === 'polygon'}
        onClick={() => onShapeStart('polygon')}
        tooltip="Draw Polygon"
      >
        <PolygonIcon className="w-5 h-5" />
      </DrawingButton>
      
      <DrawingButton
        active={activeDrawing === 'rectangle'}
        onClick={() => onShapeStart('rectangle')}
        tooltip="Draw Rectangle"
      >
        <SquareIcon className="w-5 h-5" />
      </DrawingButton>
      
      <DrawingButton
        onClick={() => onDelete()}
        tooltip="Delete Shape"
        variant="danger"
      >
        <TrashIcon className="w-5 h-5" />
      </DrawingButton>
    </div>
  );
};

// Drawing Button Component
interface DrawingButtonProps {
  active?: boolean;
  onClick: () => void;
  tooltip: string;
  variant?: 'default' | 'danger';
  children: React.ReactNode;
}

const DrawingButton: React.FC<DrawingButtonProps> = ({
  active = false,
  onClick,
  tooltip,
  variant = 'default',
  children
}) => {
  const baseClasses = "w-10 h-10 flex items-center justify-center rounded-md border transition-colors group relative";
  const variantClasses = {
    default: active 
      ? "bg-atlas-primary border-atlas-primary text-white" 
      : "bg-atlas-card border-border text-text-secondary hover:bg-atlas-secondary hover:text-text-primary",
    danger: "bg-atlas-card border-border text-danger hover:bg-danger hover:text-white"
  };

  return (
    <button
      onClick={onClick}
      className={`${baseClasses} ${variantClasses[variant]}`}
      title={tooltip}
    >
      {children}
      
      {/* Tooltip */}
      <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap">
        {tooltip}
      </div>
    </button>
  );
};
```

#### Zoom Controls Styling
```typescript
// src/components/map/ZoomControls.tsx
export const ZoomControls: React.FC<ZoomControlsProps> = ({ onZoomIn, onZoomOut }) => {
  return (
    <div className="absolute bottom-4 left-4 z-[1000] flex flex-col gap-1">
      <button
        onClick={onZoomIn}
        className="w-10 h-10 bg-atlas-card border border-border text-text-secondary hover:bg-atlas-secondary hover:text-text-primary rounded-t-md transition-colors flex items-center justify-center"
        title="Zoom In"
      >
        <PlusIcon className="w-5 h-5" />
      </button>
      
      <button
        onClick={onZoomOut}
        className="w-10 h-10 bg-atlas-card border border-border text-text-secondary hover:bg-atlas-secondary hover:text-text-primary rounded-b-md transition-colors flex items-center justify-center"
        title="Zoom Out"
      >
        <MinusIcon className="w-5 h-5" />
      </button>
    </div>
  );
};
```

### 3. Feature Components

#### AOI Panel Styling
```typescript
// src/components/features/AOIPanel.tsx
export const AOIPanel: React.FC<AOIPanelProps> = ({ aoi, onClear, onRun, isProcessing }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-text-primary">Area of Interest</h3>
        <button className="w-8 h-8 flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-atlas-secondary rounded-md transition-colors">
          <CogIcon className="w-5 h-5" />
        </button>
      </div>
      
      <div className="card-body space-y-4">
        {/* Design Upload Accordion */}
        <Accordion>
          <AccordionTrigger className="flex items-center justify-between w-full text-left">
            <span className="font-medium text-text-primary">Upload Design</span>
            <ChevronDownIcon className="w-4 h-4 text-text-secondary" />
          </AccordionTrigger>
          <AccordionContent>
            <DesignUpload />
          </AccordionContent>
        </Accordion>
        
        {/* AOI Information */}
        <Accordion defaultOpen>
          <AccordionTrigger>
            <span className="font-medium text-text-primary">Area of Interest</span>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-2">
              <div className="text-sm">
                <span className="text-text-secondary">Area: </span>
                <span className="text-text-primary">
                  {aoi ? `${aoi.area.toFixed(2)} km²` : 'No area defined'}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-text-secondary">Coordinates: </span>
                <span className="text-text-primary font-mono text-xs">
                  {aoi ? formatCoordinates(aoi.bounds) : 'None'}
                </span>
              </div>
            </div>
          </AccordionContent>
        </Accordion>
        
        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onClear}
            className="btn btn-ghost"
            disabled={!aoi}
          >
            Clear
          </button>
          <button
            onClick={onRun}
            className="btn btn-primary"
            disabled={!aoi || isProcessing}
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4" />
                Run
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
```

### 4. Modal Components

#### Settings Modal Styling
```typescript
// src/components/features/SettingsModal.tsx
export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, settings, onSave }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="modal-panel">
        <div className="modal-header">
          <h2 className="text-xl font-semibold text-text-primary flex items-center gap-2">
            <CogIcon className="w-6 h-6" />
            Configuration Settings
          </h2>
          <div className="flex items-center gap-2">
            <button onClick={onClose} className="btn btn-secondary btn-sm">
              Cancel
            </button>
            <button onClick={onSave} className="btn btn-primary btn-sm">
              Apply
            </button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Output Format Section */}
          <div>
            <h3 className="text-lg font-medium text-text-primary mb-3">Output Format</h3>
            <div className="grid grid-cols-3 gap-3">
              <RadioOption value="kmz" checked={settings.outputFormat === 'kmz'}>
                KMZ (Google Earth)
              </RadioOption>
              <RadioOption value="geojson" checked={settings.outputFormat === 'geojson'}>
                GeoJSON
              </RadioOption>
              <RadioOption value="csv" checked={settings.outputFormat === 'csv'}>
                CSV
              </RadioOption>
            </div>
          </div>
          
          {/* Data Sources Section */}
          <div>
            <h3 className="text-lg font-medium text-text-primary mb-3">Data Sources</h3>
            <div className="space-y-3">
              {Object.entries(settings.dataSources).map(([key, config]) => (
                <ToggleOption
                  key={key}
                  label={formatDataSourceName(key)}
                  checked={config.enabled}
                  onChange={(enabled) => updateDataSource(key, { enabled })}
                />
              ))}
            </div>
          </div>
          
          {/* Processing Options */}
          <div>
            <h3 className="text-lg font-medium text-text-primary mb-3">Processing Options</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Min Building Area (m²)
                </label>
                <input
                  type="number"
                  className="form-input"
                  value={settings.filters.minBuildingArea}
                  onChange={(e) => updateFilter('minBuildingArea', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Simplification Tolerance
                </label>
                <input
                  type="number"
                  step="0.001"
                  className="form-input"
                  value={settings.filters.simplificationTolerance}
                  onChange={(e) => updateFilter('simplificationTolerance', e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};
```

## Reusable UI Components

### 1. Accordion Component
```typescript
// src/components/ui/Accordion.tsx
interface AccordionProps {
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export const Accordion: React.FC<AccordionProps> = ({ children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-border rounded-md">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { isOpen, setIsOpen } as any);
        }
        return child;
      })}
    </div>
  );
};

export const AccordionTrigger: React.FC<{ children: React.ReactNode; isOpen?: boolean; setIsOpen?: (open: boolean) => void }> = ({ 
  children, 
  isOpen, 
  setIsOpen 
}) => {
  return (
    <button
      onClick={() => setIsOpen?.(!isOpen)}
      className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-atlas-secondary transition-colors"
    >
      {children}
      <ChevronDownIcon className={`w-4 h-4 text-text-secondary transition-transform ${isOpen ? 'rotate-180' : ''}`} />
    </button>
  );
};

export const AccordionContent: React.FC<{ children: React.ReactNode; isOpen?: boolean }> = ({ 
  children, 
  isOpen 
}) => {
  return (
    <div className={`px-4 pb-3 ${isOpen ? 'block' : 'hidden'}`}>
      {children}
    </div>
  );
};
```

### 2. Toggle Component
```typescript
// src/components/ui/Toggle.tsx
interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  description?: string;
  disabled?: boolean;
}

export const Toggle: React.FC<ToggleProps> = ({ 
  checked, 
  onChange, 
  label, 
  description, 
  disabled = false 
}) => {
  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-text-primary">{label}</span>
          {disabled && (
            <span className="text-xs text-text-secondary bg-atlas-secondary px-2 py-0.5 rounded">
              Disabled
            </span>
          )}
        </div>
        {description && (
          <p className="text-xs text-text-secondary mt-1">{description}</p>
        )}
      </div>
      
      <button
        type="button"
        onClick={() => !disabled && onChange(!checked)}
        disabled={disabled}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-atlas-primary focus:ring-offset-2 ${
          checked ? 'bg-atlas-primary' : 'bg-gray-600'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
};
```

### 3. Loading Spinner Component
```typescript
// src/components/ui/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div
      className={`${sizeClasses[size]} border-2 border-text-secondary border-t-transparent rounded-full animate-spin ${className}`}
    />
  );
};
```

### 4. Toast Notification Component
```typescript
// src/components/ui/Toast.tsx
import { toast as hotToast } from 'react-hot-toast';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/solid';

const iconMap = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
};

const colorMap = {
  success: 'text-success',
  error: 'text-danger',
  warning: 'text-warning',
  info: 'text-atlas-primary',
};

interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  description?: string;
}

const ToastComponent: React.FC<ToastProps> = ({ type, message, description }) => {
  const Icon = iconMap[type];
  
  return (
    <div className="flex items-start gap-3 p-4 bg-atlas-card border border-border rounded-lg shadow-atlas-md max-w-sm">
      <Icon className={`w-5 h-5 ${colorMap[type]} flex-shrink-0 mt-0.5`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary">{message}</p>
        {description && (
          <p className="text-xs text-text-secondary mt-1">{description}</p>
        )}
      </div>
    </div>
  );
};

// Toast utility functions
export const toast = {
  success: (message: string, description?: string) => {
    hotToast.custom(<ToastComponent type="success" message={message} description={description} />);
  },
  error: (message: string, description?: string) => {
    hotToast.custom(<ToastComponent type="error" message={message} description={description} />);
  },
  warning: (message: string, description?: string) => {
    hotToast.custom(<ToastComponent type="warning" message={message} description={description} />);
  },
  info: (message: string, description?: string) => {
    hotToast.custom(<ToastComponent type="info" message={message} description={description} />);
  },
};
```

## Animation and Transitions

### 1. Framer Motion Integration (Optional)
```typescript
// src/components/ui/AnimatedCard.tsx
import { motion } from 'framer-motion';

export const AnimatedCard: React.FC<{ children: React.ReactNode; delay?: number }> = ({ 
  children, 
  delay = 0 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      className="card"
    >
      {children}
    </motion.div>
  );
};

export const AnimatedModal: React.FC<{ isOpen: boolean; children: React.ReactNode }> = ({ 
  isOpen, 
  children 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isOpen ? 1 : 0 }}
      transition={{ duration: 0.2 }}
      className="modal-overlay"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: isOpen ? 1 : 0.95, opacity: isOpen ? 1 : 0 }}
        transition={{ duration: 0.2 }}
        className="modal-panel"
      >
        {children}
      </motion.div>
    </motion.div>
  );
};
```

## Responsive Design

### 1. Mobile-First Approach
```typescript
// src/components/layout/ResponsiveLayout.tsx
export const ResponsiveLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-atlas-page">
      {/* Mobile sidebar overlay */}
      <div className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-black opacity-50" onClick={() => setSidebarOpen(false)} />
        <div className="relative flex flex-col w-64 h-full bg-atlas-sidebar border-r border-border">
          <Sidebar />
        </div>
      </div>
      
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <Sidebar />
      </div>
      
      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};
```

### 2. Responsive Map Layout
```typescript
// src/components/map/ResponsiveMapLayout.tsx
export const ResponsiveMapLayout: React.FC = () => {
  return (
    <div className="flex flex-col lg:flex-row h-full">
      {/* Control Panel - Top on mobile, left on desktop */}
      <div className="w-full lg:w-88 bg-atlas-sidebar border-b lg:border-b-0 lg:border-r border-border flex-shrink-0">
        <div className="h-48 lg:h-full overflow-y-auto">
          <AOIPanel />
          <ResultsPanel />
        </div>
      </div>
      
      {/* Map Container */}
      <div className="flex-1 relative">
        <MapContainer />
      </div>
    </div>
  );
};
```

## Dark Theme Implementation

### 1. Theme Provider
```typescript
// src/contexts/ThemeContext.tsx
interface ThemeContextType {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
```

## Performance Considerations

### 1. CSS-in-JS Optimization
```typescript
// src/styles/styled-components.ts (if using styled-components)
import styled, { css } from 'styled-components';

// Use theme-based styling
const Button = styled.button<{ variant: 'primary' | 'secondary' }>`
  ${({ theme, variant }) => css`
    background-color: ${variant === 'primary' ? theme.colors.atlas.primary : theme.colors.atlas.secondary};
    color: ${theme.colors.text.primary};
    border: 1px solid ${theme.colors.border.default};
    
    &:hover {
      background-color: ${variant === 'primary' ? theme.colors.blue[600] : theme.colors.atlas.secondary};
      opacity: 0.8;
    }
  `}
`;
```

### 2. Critical CSS Loading
```typescript
// src/utils/loadCSS.ts
export const loadCriticalCSS = () => {
  const criticalCSS = `
    .atlas-critical {
      background-color: #062226;
      color: #ffffff;
      font-family: Inter, system-ui, sans-serif;
    }
  `;
  
  const style = document.createElement('style');
  style.textContent = criticalCSS;
  document.head.appendChild(style);
};
```

This comprehensive styling guide provides everything needed to implement a consistent, professional design system for the Atlas React frontend while maintaining the visual identity of the current interface.
