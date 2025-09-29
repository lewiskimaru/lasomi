import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { ChevronDown, Search } from 'lucide-react';
import { Pentagon, Square, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

// Map tile sources from MAPS.md
const mapSources = {
  hybrid: {
    google: {
      name: 'Google Hybrid',
      url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
      attribution: '© Google'
    }
  },
  satellite: {
    esri: {
      name: 'Esri Satellite',
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attribution: '© Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN'
    },
    google: {
      name: 'Google Satellite',
      url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
      attribution: '© Google'
    }
  },
  street: {
    osm: {
      name: 'OpenStreetMap',
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors'
    },
    google: {
      name: 'Google Roadmap',
      url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
      attribution: '© Google'
    },
    carto_light: {
      name: 'CartoDB Light',
      url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      attribution: '© OpenStreetMap contributors, © CartoDB'
    },
    carto_dark: {
      name: 'CartoDB Dark',
      url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      attribution: '© OpenStreetMap contributors, © CartoDB'
    }
  },
  terrain: {
    opentopo: {
      name: 'OpenTopoMap',
      url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'
    },
    google: {
      name: 'Google Terrain',
      url: 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}',
      attribution: '© Google'
    },
    stamen: {
      name: 'Stamen Terrain',
      url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
      attribution: 'Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL'
    }
  }
};

interface MapComponentProps {
  onDrawingStateChange?: (isDrawing: boolean) => void;
  drawingMode?: 'polygon' | 'rectangle' | null;
  onAreaDrawn?: (area: any) => void;
}

const MapComponent: React.FC<MapComponentProps> = ({
  onDrawingStateChange,
  drawingMode,
  onAreaDrawn
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const currentLayerRef = useRef<L.TileLayer | null>(null);
  const drawingLayerRef = useRef<L.LayerGroup | null>(null);
  
  const [showLayerSelector, setShowLayerSelector] = useState(false);
  const [currentMapType, setCurrentMapType] = useState<keyof typeof mapSources>('hybrid');
  const [currentProvider, setCurrentProvider] = useState<string>('google');
  const [isDrawing, setIsDrawing] = useState(false);
  const [activeDrawingTool, setActiveDrawingTool] = useState<'polygon' | 'rectangle' | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchSuggestions, setSearchSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  
  // Advanced drawing state
  const [vertexMarkers, setVertexMarkers] = useState<L.CircleMarker[]>([]);

  // Handle manual drawing tool activation/deactivation
  const startDrawing = (mode: 'polygon' | 'rectangle') => {
    console.log('🎯 Starting drawing mode:', mode);
    console.log('🎯 Current activeDrawingTool:', activeDrawingTool);
    console.log('🎯 Map instance exists:', !!mapInstanceRef.current);
    console.log('🎯 Drawing layer exists:', !!drawingLayerRef.current);
    
    // If same tool is active, deactivate it
    if (activeDrawingTool === mode) {
      console.log('🎯 Same tool clicked, deactivating');
      deactivateDrawing();
      return;
    }
    
    setActiveDrawingTool(mode);
    onDrawingStateChange?.(true);
    
    console.log('🎯 Drawing tool activated:', mode);
    console.log('🎯 State updated, activeDrawingTool should be:', mode);
    
    // Show toast notification
    if (mode === 'polygon') {
      toast.info('Polygon drawing activated', {
        description: 'Click on the map to add vertices. Click first vertex to complete.'
      });
    } else if (mode === 'rectangle') {
      toast.info('Rectangle drawing activated', {
        description: 'Click and drag on the map to draw a rectangle.'
      });
    }
  };

  // Deactivate current drawing mode
  const deactivateDrawing = () => {
    setActiveDrawingTool(null);
    setIsDrawing(false);
    onDrawingStateChange?.(false);
    
    if (mapInstanceRef.current) {
      mapInstanceRef.current.getContainer().style.cursor = '';
    }
    
    toast.info('Drawing tool deactivated');
  };

  // Create vertex markers for editing
  const createVertexMarkers = (shape: L.Polygon) => {
    if (!mapInstanceRef.current || !drawingLayerRef.current) return [];

    const map = mapInstanceRef.current;
    const drawingLayer = drawingLayerRef.current;
    
    const latLngs = shape.getLatLngs()[0] as L.LatLng[];

    const markers = latLngs.map((latLng, index) => {
      const marker = L.circleMarker(latLng, {
        radius: 8,
        color: '#ffffff',
        fillColor: '#ff6b35',
        fillOpacity: 1,
        weight: 3,
        className: 'vertex-marker',
        pane: 'drawingPane'
      }).addTo(drawingLayer);

      // Make vertex draggable
      marker.on('mousedown', (e) => {
        e.originalEvent?.preventDefault();
        
        const onMouseMove = (moveEvent: L.LeafletMouseEvent) => {
          const newLatLng = moveEvent.latlng;
          marker.setLatLng(newLatLng);
          updateShapeVertex(shape, index, newLatLng);
        };

        const onMouseUp = () => {
          map.off('mousemove', onMouseMove);
          map.off('mouseup', onMouseUp);
          toast.success('Vertex moved');
        };

        map.on('mousemove', onMouseMove);
        map.on('mouseup', onMouseUp);
      });

      // Right-click to delete vertex (for polygons with >3 vertices)
      marker.on('contextmenu', (e) => {
        e.originalEvent?.preventDefault();
        const currentLatLngs = shape.getLatLngs()[0] as L.LatLng[];
        if (currentLatLngs.length > 3) {
          deleteVertex(shape, index);
        } else {
          toast.warning('Cannot delete vertex', {
            description: 'Polygon must have at least 3 vertices.'
          });
        }
      });

      // Hover effects
      marker.on('mouseover', () => {
        marker.setStyle({ radius: 10, fillColor: '#ff4500' });
      });
      
      marker.on('mouseout', () => {
        marker.setStyle({ radius: 8, fillColor: '#ff6b35' });
      });

      return marker;
    });

    return markers;
  };

  // Update shape vertex position
  const updateShapeVertex = (shape: L.Polygon, index: number, newLatLng: L.LatLng) => {
    const latLngs = [...(shape.getLatLngs()[0] as L.LatLng[])];
    latLngs[index] = newLatLng;
    shape.setLatLngs([latLngs]);
  };

  // Delete vertex from polygon
  const deleteVertex = (shape: L.Polygon, index: number) => {
    const latLngs = [...(shape.getLatLngs()[0] as L.LatLng[])];
    latLngs.splice(index, 1);
    shape.setLatLngs([latLngs]);
    
    // Recreate vertex markers
    clearVertexMarkers();
    const newMarkers = createVertexMarkers(shape);
    setVertexMarkers(newMarkers);
    
    toast.success('Vertex deleted');
  };

  // Clear vertex markers
  const clearVertexMarkers = () => {
    vertexMarkers.forEach(marker => marker.remove());
    setVertexMarkers([]);
  };

  // Enable vertex editing mode
  const enableVertexEditing = (shape: L.Polygon) => {
    clearVertexMarkers();
    const markers = createVertexMarkers(shape);
    setVertexMarkers(markers);
    
    toast.info('Vertex editing enabled', {
      description: 'Drag vertices to adjust shape. Right-click to delete vertices.'
    });
  };

  // Progressive search functionality based on atlas.js
  const performProgressiveSearch = async (query: string) => {
    const trimmedQuery = query.trim();
    
    if (trimmedQuery.length < 2) {
      setShowSuggestions(false);
      setSearchSuggestions([]);
      return;
    }
    
    setIsSearchLoading(true);
    
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(trimmedQuery)}&limit=5&addressdetails=1`
      );
      const results = await response.json();
      
      if (results.length > 0) {
        setSearchSuggestions(results);
        setShowSuggestions(true);
        setSelectedSuggestionIndex(-1); // Reset selection
      } else {
        setSearchSuggestions([]);
        setShowSuggestions(true); // Show "no results" message
        setSelectedSuggestionIndex(-1);
      }
    } catch (error) {
      console.error('Search error:', error);
      setShowSuggestions(false);
      setSearchSuggestions([]);
      setSelectedSuggestionIndex(-1);
      toast.error('Search failed', {
        description: 'Unable to search locations. Please try again.'
      });
    } finally {
      setIsSearchLoading(false);
    }
  };

  // Handle search result selection
  const selectSearchResult = (lat: number, lon: number, name: string) => {
    if (!mapInstanceRef.current) return;

    // Center map on selected location
    mapInstanceRef.current.setView([lat, lon], 15);
    
    // Update search input with selected name
    const displayName = name.split(',').slice(0, 3).join(', ');
    setSearchQuery(displayName);
    
    // Hide suggestions
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    
    // Add a temporary marker
    const marker = L.marker([lat, lon])
      .addTo(mapInstanceRef.current)
      .bindPopup(`<strong>${displayName}</strong><br>Coordinates: ${lat.toFixed(4)}, ${lon.toFixed(4)}`)
      .openPopup();
    
    // Remove marker after 5 seconds
    setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.removeLayer(marker);
      }
    }, 5000);
    
    toast.success('Location found', {
      description: `Zoomed to ${displayName}`
    });
  };

  // Handle search input with debounce (progressive search)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.trim()) {
        performProgressiveSearch(searchQuery);
      } else {
        setShowSuggestions(false);
        setSearchSuggestions([]);
        setSelectedSuggestionIndex(-1);
      }
    }, 300); // Reduced debounce for more responsive search

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Handle clicks outside search to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const searchContainer = document.querySelector('.search-container');
      if (searchContainer && !searchContainer.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Create map instance
    const map = L.map(mapRef.current, {
      center: [-1.2921, 36.8219], // Nairobi, Kenya
      zoom: 13,
      zoomControl: false, // We'll add it back with custom position
      attributionControl: true
    });

    // Add zoom control to bottom-left
    L.control.zoom({
      position: 'bottomleft'
    }).addTo(map);

    // Create custom pane for drawings with high z-index
    map.createPane('drawingPane');
    const drawingPane = map.getPane('drawingPane')!;
    drawingPane.style.zIndex = '650'; // Higher than overlays (400) but lower than controls (700)
    drawingPane.style.pointerEvents = 'auto';
    
    console.log('Created drawing pane with z-index:', drawingPane.style.zIndex);
    console.log('Drawing pane element:', drawingPane);

    // Create initial tile layer
    const initialSources = mapSources[currentMapType] as any;
    const initialSource = initialSources[currentProvider];
    const tileLayer = L.tileLayer(initialSource.url, {
      attribution: initialSource.attribution,
      maxZoom: 19
    });

    tileLayer.addTo(map);
    currentLayerRef.current = tileLayer;

    // Create drawing layer group with custom pane
    const drawingLayer = L.layerGroup().addTo(map);
    drawingLayerRef.current = drawingLayer;
    
    console.log('✅ Created drawing layer group:', drawingLayer);
    console.log('✅ Drawing layer added to map');

    mapInstanceRef.current = map;

    // Add direct DOM click listener for testing
    const mapContainer = map.getContainer();
    const domClickHandler = (e: MouseEvent) => {
      console.log('🟣 DOM click on map container detected!', e);
    };
    mapContainer.addEventListener('click', domClickHandler);
    
    console.log('🟣 Added DOM click listener to map container');

    // Cleanup function
    return () => {
      clearVertexMarkers();
      // Remove DOM click listener
      mapContainer.removeEventListener('click', domClickHandler);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        currentLayerRef.current = null;
        drawingLayerRef.current = null;
      }
    };
  }, []);

  // Handle drawing mode changes with advanced functionality
  useEffect(() => {
    console.log('🔥 Drawing effect triggered');
    console.log('🔥 Map exists:', !!mapInstanceRef.current);
    console.log('🔥 Drawing layer exists:', !!drawingLayerRef.current);
    console.log('🔥 drawingMode prop:', drawingMode);
    console.log('🔥 activeDrawingTool state:', activeDrawingTool);
    console.log('🔥 isDrawing state:', isDrawing);
    
    if (!mapInstanceRef.current || !drawingLayerRef.current) {
      console.log('🔥 Missing map or drawing layer, exiting');
      return;
    }

    const map = mapInstanceRef.current;
    const drawingLayer = drawingLayerRef.current;
    const currentMode = drawingMode || activeDrawingTool;
    
    console.log('🔥 Current drawing mode:', currentMode);
    console.log('🔥 Drawing layer contents:', drawingLayer.getLayers().length, 'layers');

    if (currentMode && !isDrawing) {
      console.log('🔥 Starting drawing process for mode:', currentMode);
      setIsDrawing(true);
      onDrawingStateChange?.(true);

      map.getContainer().style.cursor = 'crosshair';
      
      console.log('🔥 Map container cursor set to crosshair');
      console.log('🔥 Map container element:', map.getContainer());
      console.log('🔥 Map container has click listeners:', map.getContainer().onclick !== null);

      if (currentMode === 'polygon') {
        // Advanced polygon drawing with vertex completion
        let polygonCoords: L.LatLng[] = [];
        let tempPolyline: L.Polyline | null = null;
        let startMarker: L.CircleMarker | null = null;
        let tempVertexMarkers: L.CircleMarker[] = [];

        const handleMapClick = (e: L.LeafletMouseEvent) => {
          console.log('🔴 Polygon click detected at:', e.latlng);
          console.log('🔴 Current polygon coords length:', polygonCoords.length);
          console.log('🔴 Drawing layer:', drawingLayer);
          
          if (polygonCoords.length === 0) {
            console.log('🔴 Creating start marker at:', e.latlng);
            // First vertex
            polygonCoords = [e.latlng];
            
            // Create start marker (larger, different style)
            startMarker = L.circleMarker(e.latlng, {
              radius: 10,
              color: '#ffffff',
              fillColor: '#ff6b35',
              fillOpacity: 1,
              weight: 3,
              className: 'start-vertex-marker',
              pane: 'drawingPane'
            }).addTo(drawingLayer);
            
            startMarker.on('click', completePolygon);
            startMarker.on('mouseover', () => {
              startMarker?.setStyle({ radius: 12, fillColor: '#ff4500' });
            });
            startMarker.on('mouseout', () => {
              startMarker?.setStyle({ radius: 10, fillColor: '#ff6b35' });
            });
            
            tempPolyline = L.polyline(polygonCoords, { 
              color: '#ff6b35', 
              weight: 4,
              dashArray: '10, 5',
              opacity: 1.0,
              pane: 'drawingPane',
              className: 'drawing-polyline-temp'
            }).addTo(drawingLayer);
            
            console.log('🔴 Created temp polyline:', tempPolyline);
            console.log('🔴 Temp polyline added to layer, total layers:', drawingLayer.getLayers().length);
            
          } else {
            console.log('🔴 Adding vertex at:', e.latlng);
            // Additional vertices
            polygonCoords.push(e.latlng);
            console.log('🔴 Updated polygon coords:', polygonCoords.length, 'points');
            
            // Create vertex marker
            const vertexMarker = L.circleMarker(e.latlng, {
              radius: 7,
              color: '#ffffff',
              fillColor: '#ff6b35',
              fillOpacity: 1,
              weight: 2,
              className: 'temp-vertex-marker',
              pane: 'drawingPane'
            }).addTo(drawingLayer);
            
            tempVertexMarkers.push(vertexMarker);
            tempPolyline?.setLatLngs(polygonCoords);
            
            console.log('🔴 Created vertex marker:', vertexMarker);
            console.log('🔴 Total temp vertex markers:', tempVertexMarkers.length);
            console.log('🔴 Updated polyline with coords:', polygonCoords.length);
            console.log('🔴 Total layers in drawing layer:', drawingLayer.getLayers().length);
          }
        };

        const completePolygon = () => {
          if (polygonCoords.length >= 3) {
            // Clean up temporary elements
            tempPolyline?.remove();
            startMarker?.remove();
            tempVertexMarkers.forEach(marker => marker.remove());
            
            // Create final polygon with enhanced visibility
            const finalPolygon = L.polygon(polygonCoords, { 
              color: '#ff6b35', 
              fillColor: '#ff6b35', 
              fillOpacity: 0.4,
              weight: 4,
              opacity: 1.0,
              pane: 'drawingPane',
              className: 'drawing-polygon-final'
            }).addTo(drawingLayer);
            
            console.log('Created final polygon:', finalPolygon);
            console.log('Polygon bounds:', finalPolygon.getBounds());
            
            // Enable vertex editing on the new shape
            setTimeout(() => {
              enableVertexEditing(finalPolygon);
            }, 100);
            
            onAreaDrawn?.(finalPolygon);
            toast.success('Polygon completed', {
              description: 'Polygon has been drawn successfully. Vertex editing is now enabled.'
            });
            
            finishDrawing();
          }
        };

        const finishDrawing = () => {
          map.off('click', handleMapClick);
          map.getContainer().style.cursor = '';
          setIsDrawing(false);
          setActiveDrawingTool(null);
          onDrawingStateChange?.(false);
        };

        // Handle ESC key to cancel
        const handleKeyPress = (e: KeyboardEvent) => {
          if (e.key === 'Escape') {
            tempPolyline?.remove();
            startMarker?.remove();
            tempVertexMarkers.forEach(marker => marker.remove());
            finishDrawing();
            toast.info('Polygon drawing cancelled');
          }
        };

        // Add a test handler to see if ANY map events work
        const testClickHandler = (e: L.LeafletMouseEvent) => {
          console.log('🟢 TEST: Map click detected at:', e.latlng);
        };
        
        const testMouseMoveHandler = (e: L.LeafletMouseEvent) => {
          console.log('🟡 TEST: Mouse move on map:', e.latlng);
        };
        
        map.on('click', handleMapClick);
        map.on('click', testClickHandler); // Additional test handler
        map.on('mousemove', testMouseMoveHandler); // Test mouse moves
        document.addEventListener('keydown', handleKeyPress);
        
        console.log('🔴 Attached polygon click handler to map');
        console.log('🔴 Map click handlers attached successfully');
        console.log('🔴 Testing if map events work at all...');

        // Cleanup function
        return () => {
          map.off('click', handleMapClick);
          map.off('click', testClickHandler);
          map.off('mousemove', testMouseMoveHandler);
          document.removeEventListener('keydown', handleKeyPress);
          tempPolyline?.remove();
          startMarker?.remove();
          tempVertexMarkers.forEach(marker => marker.remove());
        };

      } else if (currentMode === 'rectangle') {
        console.log('🔵 Initializing rectangle drawing mode');
        // Enhanced rectangle drawing
        let isDrawingRect = false;
        let startPoint: L.LatLng | null = null;
        let tempRectangle: L.Rectangle | null = null;

        const handleMapMouseDown = (e: L.LeafletMouseEvent) => {
          console.log('🔵 Rectangle mousedown at:', e.latlng);
          isDrawingRect = true;
          startPoint = e.latlng;
          console.log('🔵 Rectangle drawing started');
        };

        const handleMapMouseMove = (e: L.LeafletMouseEvent) => {
          if (isDrawingRect && startPoint) {
            console.log('🔵 Rectangle mousemove, drawing temp rectangle');
            tempRectangle?.remove();
            const bounds = L.latLngBounds(startPoint, e.latlng);
            tempRectangle = L.rectangle(bounds, { 
              color: '#ff6b35', 
              fillColor: '#ff6b35', 
              fillOpacity: 0.3,
              weight: 3,
              dashArray: '8, 8',
              opacity: 0.8,
              pane: 'drawingPane'
            }).addTo(drawingLayer);
            console.log('🔵 Temp rectangle created:', tempRectangle);
            console.log('🔵 Drawing layer now has:', drawingLayer.getLayers().length, 'layers');
          }
        };

        const handleMapMouseUp = () => {
          if (isDrawingRect && tempRectangle) {
            // Replace temporary with final rectangle
            const bounds = tempRectangle.getBounds();
            tempRectangle.remove();
            
            const finalRectangle = L.rectangle(bounds, {
              color: '#ff6b35', 
              fillColor: '#ff6b35', 
              fillOpacity: 0.4,
              weight: 4,
              opacity: 1.0,
              pane: 'drawingPane',
              className: 'drawing-rectangle-final'
            }).addTo(drawingLayer);
            
            console.log('Created final rectangle:', finalRectangle);
            
            // Note: Rectangle vertex editing not implemented yet
            // Focus on polygon editing for now
            
            onAreaDrawn?.(finalRectangle);
            toast.success('Rectangle completed', {
              description: 'Rectangle has been drawn successfully.'
            });
            finishDrawing();
          }
        };

        const finishDrawing = () => {
          map.off('mousedown', handleMapMouseDown);
          map.off('mousemove', handleMapMouseMove);
          map.off('mouseup', handleMapMouseUp);
          map.getContainer().style.cursor = '';
          setIsDrawing(false);
          setActiveDrawingTool(null);
          onDrawingStateChange?.(false);
        };

        map.on('mousedown', handleMapMouseDown);
        map.on('mousemove', handleMapMouseMove);
        map.on('mouseup', handleMapMouseUp);
        
        console.log('🔵 Attached rectangle drawing handlers to map');

        // Cleanup function
        return () => {
          map.off('mousedown', handleMapMouseDown);
          map.off('mousemove', handleMapMouseMove);
          map.off('mouseup', handleMapMouseUp);
          tempRectangle?.remove();
        };
      }
    }
  }, [drawingMode, activeDrawingTool, isDrawing]);
  
  // Add logging for state changes
  useEffect(() => {
    console.log('🏁 Drawing state changed:');
    console.log('  - activeDrawingTool:', activeDrawingTool);
    console.log('  - isDrawing:', isDrawing);
    console.log('  - drawingMode prop:', drawingMode);
  }, [activeDrawingTool, isDrawing, drawingMode]);

  // Change map layer
  const changeMapLayer = (mapType: keyof typeof mapSources, provider: string) => {
    if (!mapInstanceRef.current || !currentLayerRef.current) return;

    const map = mapInstanceRef.current;
    const sources = mapSources[mapType] as any;
    const newSource = sources[provider];

    if (newSource) {
      // Remove current layer
      currentLayerRef.current.remove();

      // Add new layer
      const newTileLayer = L.tileLayer(newSource.url, {
        attribution: newSource.attribution,
        maxZoom: 19
      });

      newTileLayer.addTo(map);
      currentLayerRef.current = newTileLayer;

      setCurrentMapType(mapType);
      setCurrentProvider(provider);
      setShowLayerSelector(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showLayerSelector) {
        const target = event.target as Element;
        if (!target.closest('.map-provider-selector')) {
          setShowLayerSelector(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showLayerSelector]);

  // Clear all drawings
  const clearDrawings = () => {
    if (drawingLayerRef.current) {
      drawingLayerRef.current.clearLayers();
      clearVertexMarkers();
      toast.success('Drawings cleared', {
        description: 'All drawings have been removed from the map.'
      });
    }
  };

  return (
    <div className="relative w-full h-full bg-lasomi-card border border-border rounded-lg shadow-lasomi-sm overflow-hidden">
      {/* Top Control Bar */}
      <div className="absolute top-5 left-5 right-5 z-[1000] flex items-center justify-between gap-5 pointer-events-none">
        {/* Child elements will have pointer-events: auto via CSS class */}
        {/* Drawing Tools - Left (Horizontal) */}
        <div className="bg-white/90 border border-gray-300 rounded-md shadow-md flex h-[42px] overflow-hidden interactive-child">
          <button
            onClick={() => {
              console.log('🎯 Polygon button clicked!');
              startDrawing('polygon');
            }}
            disabled={isDrawing && activeDrawingTool !== 'polygon'}
            className={`h-full px-3 flex items-center justify-center border-r border-gray-300 last:border-r-0 transition-colors ${
              activeDrawingTool === 'polygon' 
                ? 'bg-blue-100 text-blue-700' 
                : 'hover:bg-gray-100 text-gray-700'
            } ${isDrawing && activeDrawingTool !== 'polygon' ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            title="Draw Polygon"
          >
            <Pentagon className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => {
              console.log('🎯 Rectangle button clicked!');
              startDrawing('rectangle');
            }}
            disabled={isDrawing && activeDrawingTool !== 'rectangle'}
            className={`h-full px-3 flex items-center justify-center border-r border-gray-300 last:border-r-0 transition-colors ${
              activeDrawingTool === 'rectangle' 
                ? 'bg-blue-100 text-blue-700' 
                : 'hover:bg-gray-100 text-gray-700'
            } ${isDrawing && activeDrawingTool !== 'rectangle' ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            title="Draw Rectangle"
          >
            <Square className="w-5 h-5" />
          </button>
          
          <button
            onClick={clearDrawings}
            className="h-full px-3 flex items-center justify-center hover:bg-red-50 hover:text-red-600 text-gray-700 transition-colors cursor-pointer"
            title="Clear All Drawings"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar - Center */}
        <div className="flex-1 max-w-md mx-4 interactive-child">
          <div className="relative search-container">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search locations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setSearchFocused(true)}
              onBlur={() => {
                // Delay hiding suggestions to allow clicking on them
                setTimeout(() => setSearchFocused(false), 200);
              }}
              onKeyDown={(e) => {
                if (!showSuggestions || searchSuggestions.length === 0) return;
                
                if (e.key === 'ArrowDown') {
                  e.preventDefault();
                  setSelectedSuggestionIndex(prev => 
                    prev < searchSuggestions.length - 1 ? prev + 1 : prev
                  );
                } else if (e.key === 'ArrowUp') {
                  e.preventDefault();
                  setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
                } else if (e.key === 'Enter' && selectedSuggestionIndex >= 0) {
                  e.preventDefault();
                  const result = searchSuggestions[selectedSuggestionIndex];
                  selectSearchResult(parseFloat(result.lat), parseFloat(result.lon), result.display_name);
                } else if (e.key === 'Escape') {
                  setShowSuggestions(false);
                  setSelectedSuggestionIndex(-1);
                }
              }}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md bg-white/90 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
            
            {/* Search Suggestions Dropdown */}
            {showSuggestions && (searchFocused || searchSuggestions.length > 0) && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-64 overflow-y-auto z-[1001]">
                {isSearchLoading ? (
                  <div className="px-3 py-2 text-sm text-gray-500 flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                    Searching...
                  </div>
                ) : searchSuggestions.length > 0 ? (
                  searchSuggestions.map((result, index) => {
                    const displayName = result.display_name.split(',').slice(0, 3).join(', ');
                    const type = result.type || result.class || 'location';
                    const isSelected = index === selectedSuggestionIndex;
                    
                    return (
                      <button
                        key={index}
                        onClick={() => selectSearchResult(parseFloat(result.lat), parseFloat(result.lon), result.display_name)}
                        className={`w-full text-left px-3 py-2 transition-colors border-b border-gray-100 last:border-b-0 flex items-start gap-2 ${
                          isSelected ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-900 truncate">
                            {displayName}
                          </div>
                          <div className="text-xs text-gray-500 capitalize">
                            {type}
                          </div>
                        </div>
                      </button>
                    );
                  })
                ) : (
                  <div className="px-3 py-2 text-sm text-gray-500">
                    No locations found
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Map Provider Selector - Right */}
        <div className="map-provider-selector relative interactive-child">
          <button
            onClick={() => setShowLayerSelector(!showLayerSelector)}
            className="bg-white/90 border border-gray-300 rounded-md px-3 py-2 shadow-md hover:bg-gray-100 transition-colors flex items-center gap-2 text-sm text-gray-700 whitespace-nowrap"
          >
            <span>Map: {(mapSources[currentMapType] as any)[currentProvider]?.name || 'OpenStreetMap'}</span>
            <ChevronDown className="w-4 h-4" />
          </button>

          {/* Layer Selector Dropdown */}
          {showLayerSelector && (
            <div className="absolute top-full right-0 mt-2 bg-white border border-gray-300 rounded-md shadow-lg min-w-48 max-h-64 overflow-y-auto">
              {Object.entries(mapSources).map(([mapType, providers]) => (
                <div key={mapType}>
                  <div className="px-3 py-2 bg-gray-50 border-b border-gray-200 text-xs font-medium text-gray-600 uppercase tracking-wide">
                    {mapType}
                  </div>
                  {Object.entries(providers).map(([provider, config]) => (
                    <button
                      key={provider}
                      onClick={() => changeMapLayer(mapType as keyof typeof mapSources, provider)}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                        currentMapType === mapType && currentProvider === provider
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-700'
                      }`}
                    >
                      {(config as any).name}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Map Container */}
      <div
        ref={mapRef}
        className="w-full h-full"
        style={{ minHeight: '400px' }}
      />
    </div>
  );
};

export default MapComponent;