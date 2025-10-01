import React, { useState, useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '@geoman-io/leaflet-geoman-free';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';
import 'leaflet-geometryutil';
import { 
  Play,
  ChevronDown,
  ChevronUp,
  Upload as UploadIcon,
  FileText,
  X,
  CheckCircle2,
  Trash2,
  Square,
  Pentagon,
  Layers
} from 'lucide-react';
import type { AOIDrawingState, JobStatus } from '@/shared/types';
import { useAppSession } from '@/react-app/hooks/useStorage';
import { useStorage } from '@/react-app/context/StorageContext';
import { TreeView, type TreeNode } from '@/react-app/components/ui';
import { toast } from 'sonner';

// Map tile sources following vanilla JS
const mapSources = {
  satellite: {
    google_hybrid: {
      name: 'Google Hybrid',
      url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
      attribution: '© Google'
    },
    google_satellite: {
      name: 'Google Satellite',
      url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
      attribution: '© Google'
    },
    esri: {
      name: 'Esri World Imagery',
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attribution: '© Esri'
    }
  },
  street: {
    osm: {
      name: 'OpenStreetMap',
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors'
    },
    google: {
      name: 'Google Streets',
      url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
      attribution: '© Google'
    },
    carto_light: {
      name: 'CartoDB Light',
      url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      attribution: '© OpenStreetMap, © CartoDB'
    }
  },
  terrain: {
    opentopo: {
      name: 'OpenTopoMap',
      url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap, SRTM'
    },
    google: {
      name: 'Google Terrain',
      url: 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}',
      attribution: '© Google'
    }
  }
};

interface FeaturesState {
  aoiState: AOIDrawingState;
  jobStatus: JobStatus | null;
  dataSources: Record<string, boolean>;
}

interface UploadedDesign {
  file: File;
  layers: TreeNode[];
  processed: boolean;
}

const defaultState: FeaturesState = {
  aoiState: {
    isDrawing: false,
    drawingMode: null,
  },
  jobStatus: null,
  dataSources: {
    'google_buildings': true,
    'microsoft_buildings': false,
    'osm_buildings': false,
    'osm_roads': true,
    'osm_railways': false,
    'osm_landmarks': true,
    'osm_natural': true,
  }
};

export default function Features() {
  const { logActivity } = useStorage();
  const { 
    state: featuresState, 
    setState: setFeaturesState, 
    loading: sessionLoading 
  } = useAppSession<FeaturesState>('features', defaultState);

  // Map refs
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const drawingLayerRef = useRef<L.FeatureGroup | null>(null);
  const currentPolygonRef = useRef<L.Polygon | L.Rectangle | null>(null);
  const currentTileLayerRef = useRef<L.TileLayer | null>(null);
  // Custom polygon drawing refs
  const polygonPointsRef = useRef<L.LatLng[]>([]);
  const startMarkerRef = useRef<L.Marker | null>(null);
  const tempPolylineRef = useRef<L.Polyline | null>(null);
  const tempVertexMarkersRef = useRef<L.Marker[]>([]);
  const ghostVertexRef = useRef<L.Marker | null>(null); // Cursor follower
  const permanentVertexMarkersRef = useRef<L.Marker[]>([]); // Draggable vertices for completed shape
  const isDrawingPolygonRef = useRef<boolean>(false);
  const polygonClickHandlerRef = useRef<((e: L.LeafletMouseEvent) => void) | null>(null);
  const polygonKeydownHandlerRef = useRef<((e: KeyboardEvent) => void) | null>(null);
  const polygonMouseMoveHandlerRef = useRef<((e: L.LeafletMouseEvent) => void) | null>(null);
  // Rectangle drawing state
  const isDrawingRectRef = useRef<boolean>(false);
  const rectStartRef = useRef<L.LatLng | null>(null);
  const tempRectangleRef = useRef<L.Rectangle | null>(null);
  const rectMouseDownRef = useRef<((e: L.LeafletMouseEvent) => void) | null>(null);
  const rectMouseMoveRef = useRef<((e: L.LeafletMouseEvent) => void) | null>(null);
  const rectMouseUpRef = useRef<((e: L.LeafletMouseEvent) => void) | null>(null);

  const cleanupPolygonDraft = (map?: L.Map) => {
    tempPolylineRef.current?.remove();
    startMarkerRef.current?.remove();
    tempVertexMarkersRef.current.forEach(m => m.remove());
    ghostVertexRef.current?.remove();
    tempVertexMarkersRef.current = [];
    ghostVertexRef.current = null;
    polygonPointsRef.current = [];
    isDrawingPolygonRef.current = false;
    if (map && polygonClickHandlerRef.current) {
      map.off('click', polygonClickHandlerRef.current);
    }
    if (map && polygonMouseMoveHandlerRef.current) {
      map.off('mousemove', polygonMouseMoveHandlerRef.current);
    }
    if (polygonKeydownHandlerRef.current) {
      document.removeEventListener('keydown', polygonKeydownHandlerRef.current);
    }
    polygonClickHandlerRef.current = null;
    polygonKeydownHandlerRef.current = null;
    polygonMouseMoveHandlerRef.current = null;
  };

  const cleanupRectangleDraft = (map?: L.Map) => {
    tempRectangleRef.current?.remove();
    tempRectangleRef.current = null;
    isDrawingRectRef.current = false;
    rectStartRef.current = null;
    if (map) {
      if (rectMouseDownRef.current) map.off('mousedown', rectMouseDownRef.current);
      if (rectMouseMoveRef.current) map.off('mousemove', rectMouseMoveRef.current);
      if (rectMouseUpRef.current) map.off('mouseup', rectMouseUpRef.current);
    }
    rectMouseDownRef.current = null;
    rectMouseMoveRef.current = null;
    rectMouseUpRef.current = null;
  };

  const getPixelDistance = (map: L.Map, a: L.LatLng, b: L.LatLng) => {
    const pa = map.latLngToLayerPoint(a);
    const pb = map.latLngToLayerPoint(b);
    return pa.distanceTo(pb);
  };

  // State
  const [aoiState, setAoiState] = useState<AOIDrawingState>(featuresState.aoiState);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(featuresState.jobStatus);
  const [dataSources, setDataSources] = useState(featuresState.dataSources);
  const [uploadedDesign, setUploadedDesign] = useState<UploadedDesign | null>(null);
  
  // UI State
  const [designAccordionOpen, setDesignAccordionOpen] = useState(false);
  const [aoiAccordionOpen, setAoiAccordionOpen] = useState(true);
  const [activeDrawingMode, setActiveDrawingMode] = useState<'polygon' | 'rectangle' | null>(null);
  const [aoiArea, setAoiArea] = useState<string>('No area defined');
  const [aoiCoords, setAoiCoords] = useState<string>('None');
  const [showLayerSelector, setShowLayerSelector] = useState(false);
  const [currentMapType, setCurrentMapType] = useState<keyof typeof mapSources>('satellite');
  const [currentProvider, setCurrentProvider] = useState<string>('google_hybrid');

  // Save state to session when it changes
  useEffect(() => {
    if (!sessionLoading) {
      setFeaturesState({
        aoiState,
        jobStatus,
        dataSources
      });
    }
  }, [aoiState, jobStatus, dataSources, setFeaturesState, sessionLoading]);

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    const map = L.map(mapRef.current, { zoomControl: false }).setView([-1.2921, 36.8219], 13);
    
    // Add zoom control to bottom-left
    L.control.zoom({
      position: 'bottomleft'
    }).addTo(map);
    
    // Add tile layer
    const initialSource = (mapSources[currentMapType] as any)[currentProvider];
    const tileLayer = L.tileLayer(initialSource.url, {
      attribution: initialSource.attribution,
      maxZoom: 19
    }).addTo(map);
    currentTileLayerRef.current = tileLayer;

    // Drawing layer
    const drawingLayer = L.featureGroup().addTo(map);
    drawingLayerRef.current = drawingLayer;

    // Initialize Leaflet-Geoman
    map.pm.addControls({
      position: 'topleft',
      drawCircle: false,
      drawCircleMarker: false,
      drawPolyline: false,
      drawMarker: false,
      drawText: false,
      cutPolygon: false,
    });

    // Hide default controls, we'll use custom buttons
    map.pm.removeControls();

    // Set safe global options (no guides)
    // @ts-ignore
    map.pm.setGlobalOptions?.({
      continueDrawing: false,
      snappable: false,
      finishOn: 'click',
      pathOptions: { color: '#ff6b35', weight: 4, fill: false, opacity: 1 }
    });

    // Handle shape creation (Geoman)
    map.on('pm:create', (e) => {
      const layer = e.layer;
      drawingLayer.addLayer(layer);
      
      if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
        // Apply orange stroke and no fill
        (layer as any).setStyle?.({
          color: '#ff6b35',
          weight: 4,
          fill: false,
          opacity: 1.0
        });

        // Clear previous polygon
        if (currentPolygonRef.current) {
          drawingLayer.removeLayer(currentPolygonRef.current);
        }
        currentPolygonRef.current = layer as L.Polygon | L.Rectangle;

        // Calculate center and simple bounds
        const bounds = layer.getBounds();
        const center = bounds.getCenter();
        setAoiCoords(`${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`);
        // Persist AOI in our app shape (stringified polygon and bounds)
        setAoiState(prev => ({
          ...prev,
          currentAOI: {
            polygon: JSON.stringify(layer.toGeoJSON().geometry),
            area: 0,
            bounds: {
              north: bounds.getNorth(),
              south: bounds.getSouth(),
              east: bounds.getEast(),
              west: bounds.getWest(),
            }
          },
          isDrawing: false,
          drawingMode: null
        }));

        // Auto-deactivate the tool
        setActiveDrawingMode(null);
        setAoiState(prev => ({ ...prev, isDrawing: false, drawingMode: null }));
        // Ensure any custom polygon listeners are removed
        cleanupPolygonDraft(map);
        map.pm.disableDraw();
        toast.success('Area defined successfully');

        logActivity({
          action: 'area_drawn',
          appId: 'features',
          appName: 'Features',
          description: 'Area drawn'
        });
      }
    });

    mapInstanceRef.current = map;

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Handle drawing activation
  const enableDrawing = (mode: 'polygon' | 'rectangle') => {
    if (!mapInstanceRef.current) return;

    const map = mapInstanceRef.current;

    // If clicking same mode, deactivate
    if (activeDrawingMode === mode) {
      map.pm.disableDraw();
      setActiveDrawingMode(null);
      setAoiState(prev => ({ ...prev, isDrawing: false, drawingMode: null }));
      return;
    }

    // Before activating, cleanup any existing custom polygon state
    cleanupPolygonDraft(map);

    // Activate drawing
    if (mode === 'polygon') {
      // Custom polygon drawing: finish on clicking first vertex
      const drawingLayer = drawingLayerRef.current;
      if (!drawingLayer) return;

      // Cleanup any previous state
      tempPolylineRef.current?.remove();
      startMarkerRef.current?.remove();
      tempVertexMarkersRef.current.forEach(m => m.remove());
      tempVertexMarkersRef.current = [];
      polygonPointsRef.current = [];
      isDrawingPolygonRef.current = true;

      const finishPolygon = () => {
        const points = polygonPointsRef.current;
        if (points.length >= 3) {
          // Remove temps
          cleanupPolygonDraft(map);

          // Create final polygon
          const finalPolygon = L.polygon(points, {
            color: '#ff6b35',
            weight: 4,
            fill: false,
            opacity: 1.0
          }).addTo(drawingLayer);

          currentPolygonRef.current = finalPolygon;

          // Add permanent draggable vertex markers on completed polygon
          points.forEach((point, index) => {
            const vertexIcon = L.divIcon({
              className: 'aoi-permanent-vertex',
              html: '<div style="width:12px;height:12px;border:2px solid #ff6b35;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;cursor:move;"></div>',
              iconSize: [12, 12],
              iconAnchor: [6, 6]
            });
            const permanentMarker = L.marker(point, { 
              icon: vertexIcon, 
              interactive: true,
              draggable: true  // Enable dragging
            }).addTo(drawingLayer);

            // Hover effect to show vertices are draggable
            permanentMarker.on('mouseover', () => {
              const hoverIcon = L.divIcon({
                className: 'aoi-permanent-vertex-hover',
                html: '<div style="width:14px;height:14px;border:2px solid #ff6b35;border-radius:50%;background:#ffeee9;display:flex;align-items:center;justify-content:center;cursor:move;"></div>',
                iconSize: [14, 14],
                iconAnchor: [7, 7]
              });
              permanentMarker.setIcon(hoverIcon);
            });
            permanentMarker.on('mouseout', () => {
              permanentMarker.setIcon(vertexIcon);
            });

            // Update polygon shape when vertex is dragged
            permanentMarker.on('drag', () => {
              const newLatLng = permanentMarker.getLatLng();
              const currentLatLngs = finalPolygon.getLatLngs()[0] as L.LatLng[];
              currentLatLngs[index] = newLatLng;
              finalPolygon.setLatLngs(currentLatLngs);
            });

            // Update state when drag ends
            permanentMarker.on('dragend', () => {
              const bounds = finalPolygon.getBounds();
              const center = bounds.getCenter();
              setAoiCoords(`${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`);
              setAoiState(prev => ({
                ...prev,
                currentAOI: {
                  polygon: JSON.stringify(finalPolygon.toGeoJSON().geometry),
                  area: 0,
                  bounds: {
                    north: bounds.getNorth(),
                    south: bounds.getSouth(),
                    east: bounds.getEast(),
                    west: bounds.getWest(),
                  }
                }
              }));
              toast.success('Vertex position updated');
            });

            permanentVertexMarkersRef.current.push(permanentMarker);
          });

          // Calculate center and save bounds
          const bounds = finalPolygon.getBounds();
          const center = bounds.getCenter();
          setAoiCoords(`${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`);
          setAoiState(prev => ({
            ...prev,
            currentAOI: {
              polygon: JSON.stringify(finalPolygon.toGeoJSON().geometry),
              area: 0,
              bounds: {
                north: bounds.getNorth(),
                south: bounds.getSouth(),
                east: bounds.getEast(),
                west: bounds.getWest(),
              }
            },
            isDrawing: false,
            drawingMode: null
          }));

          setActiveDrawingMode(null);
          setAoiState(prev => ({ ...prev, isDrawing: false, drawingMode: null }));
          cleanupPolygonDraft(map);
          map.pm.disableDraw();
          toast.success('Polygon completed');
        }
      };

      const handleMapClick = (e: L.LeafletMouseEvent) => {
        // First point
        if (polygonPointsRef.current.length === 0) {
          polygonPointsRef.current = [e.latlng];

          // Start marker - always shows + (stays + until hover when finishable)
          const startIcon = L.divIcon({
            className: 'aoi-start-vertex',
            html: '<div style="width:16px;height:16px;border:2px solid #ff6b35;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:#ff6b35;font-weight:700;font-size:14px;cursor:pointer;">+</div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
          });
          const start = L.marker(e.latlng, { icon: startIcon, interactive: true }).addTo(drawingLayer);
          startMarkerRef.current = start;

          // Hover effect for start marker (only shows ✓ on hover when finishable)
          start.on('mouseover', () => {
            if (polygonPointsRef.current.length >= 3) {
              // Show ✓ when hovering and finishable
              const finishIconHover = L.divIcon({
                className: 'aoi-start-vertex-hover',
                html: '<div style="width:20px;height:20px;border:3px solid #2e7d32;border-radius:50%;background:#e8f5e9;display:flex;align-items:center;justify-content:center;color:#2e7d32;font-weight:700;font-size:16px;cursor:pointer;">✓</div>',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
              });
              start.setIcon(finishIconHover);
            }
          });
          start.on('mouseout', () => {
            // Always go back to + when not hovering
            const plusIcon = L.divIcon({
              className: 'aoi-start-vertex',
              html: '<div style="width:16px;height:16px;border:2px solid #ff6b35;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:#ff6b35;font-weight:700;font-size:14px;cursor:pointer;">+</div>',
              iconSize: [16, 16],
              iconAnchor: [8, 8]
            });
            start.setIcon(plusIcon);
          });

          start.on('click', (ev) => {
            // prevent adding another point via map click
            (ev as any).originalEvent?.stopPropagation?.();
            if (polygonPointsRef.current.length >= 3) {
              finishPolygon();
            }
          });

          // Temp polyline
          const temp = L.polyline([e.latlng], {
            color: '#ff6b35',
            weight: 3,
            dashArray: '8,4',
            opacity: 1.0
          }).addTo(drawingLayer);
          tempPolylineRef.current = temp;
          return;
        }

        // Additional vertices
        polygonPointsRef.current.push(e.latlng);
        tempPolylineRef.current?.setLatLngs(polygonPointsRef.current);

        // Vertex marker rendered as a plus sign inside a circle
        const vertexIcon = L.divIcon({
          className: 'aoi-vertex',
          html: '<div style="width:14px;height:14px;border:2px solid #ff6b35;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:#ff6b35;font-weight:700;font-size:12px;">+</div>',
          iconSize: [14, 14],
          iconAnchor: [7, 7]
        });
        const vm = L.marker(e.latlng, { icon: vertexIcon, interactive: false }).addTo(drawingLayer);
        tempVertexMarkersRef.current.push(vm);

        // If user clicked near the first vertex, auto-finish polygon
        try {
          const first = polygonPointsRef.current[0];
          const distPx = getPixelDistance(map, e.latlng, first);
          if (distPx <= 14) {
            finishPolygon();
          }
        } catch { /* ignore */ }
      };

      // Mouse move handler - show ghost vertex following cursor
      const handleMouseMove = (e: L.LeafletMouseEvent) => {
        if (polygonPointsRef.current.length === 0) return;

        // Create or update ghost vertex marker
        if (!ghostVertexRef.current) {
          const ghostIcon = L.divIcon({
            className: 'aoi-ghost-vertex',
            html: '<div style="width:14px;height:14px;border:2px dashed #ff6b35;border-radius:50%;background:rgba(255,255,255,0.7);display:flex;align-items:center;justify-content:center;color:#ff6b35;font-weight:700;font-size:12px;">+</div>',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          });
          const ghost = L.marker(e.latlng, { 
            icon: ghostIcon, 
            interactive: false,
            keyboard: false
          }).addTo(drawingLayer);
          ghostVertexRef.current = ghost;
        } else {
          ghostVertexRef.current.setLatLng(e.latlng);
        }

        // Update temporary polyline to include ghost position
        if (tempPolylineRef.current) {
          const allPoints = [...polygonPointsRef.current, e.latlng];
          tempPolylineRef.current.setLatLngs(allPoints);
        }
      };

      const onKeyDown = (ke: KeyboardEvent) => {
        if (ke.key === 'Escape') {
          // Cancel
          cleanupPolygonDraft(map);
          setActiveDrawingMode(null);
          setAoiState(prev => ({ ...prev, isDrawing: false, drawingMode: null }));
          toast.info('Polygon drawing cancelled');
        }
      };

      map.on('click', handleMapClick);
      map.on('mousemove', handleMouseMove);
      document.addEventListener('keydown', onKeyDown);
      polygonClickHandlerRef.current = handleMapClick;
      polygonMouseMoveHandlerRef.current = handleMouseMove;
      polygonKeydownHandlerRef.current = onKeyDown;
    } else if (mode === 'rectangle') {
      // Custom rectangle drawing to guarantee finish and deactivation
      const drawingLayer = drawingLayerRef.current;
      if (!drawingLayer) return;
      // no guide text

      const onMouseDown = (ev: L.LeafletMouseEvent) => {
        isDrawingRectRef.current = true;
        rectStartRef.current = ev.latlng;
      };
      const onMouseMove = (ev: L.LeafletMouseEvent) => {
        if (!isDrawingRectRef.current || !rectStartRef.current) return;
        tempRectangleRef.current?.remove();
        const bounds = L.latLngBounds(rectStartRef.current, ev.latlng);
        tempRectangleRef.current = L.rectangle(bounds, {
          color: '#ff6b35', weight: 4, fill: false, opacity: 1
        }).addTo(drawingLayer);
      };
      const onMouseUp = () => {
        if (!isDrawingRectRef.current || !rectStartRef.current || !tempRectangleRef.current) {
          cleanupRectangleDraft(map);
          return;
        }
        const finalRect = L.rectangle(tempRectangleRef.current.getBounds(), {
          color: '#ff6b35', weight: 4, fill: false, opacity: 1
        }).addTo(drawingLayer);
        currentPolygonRef.current = finalRect as any;

        // Add permanent draggable vertex markers for rectangle corners
        const bounds = finalRect.getBounds();
        const corners = [
          bounds.getNorthWest(),
          bounds.getNorthEast(),
          bounds.getSouthEast(),
          bounds.getSouthWest()
        ];

        corners.forEach((corner, index) => {
          const vertexIcon = L.divIcon({
            className: 'aoi-permanent-vertex',
            html: '<div style="width:12px;height:12px;border:2px solid #ff6b35;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;cursor:move;"></div>',
            iconSize: [12, 12],
            iconAnchor: [6, 6]
          });
          const permanentMarker = L.marker(corner, { 
            icon: vertexIcon, 
            interactive: true,
            draggable: true
          }).addTo(drawingLayer);

          // Hover effect
          permanentMarker.on('mouseover', () => {
            const hoverIcon = L.divIcon({
              className: 'aoi-permanent-vertex-hover',
              html: '<div style="width:14px;height:14px;border:2px solid #ff6b35;border-radius:50%;background:#ffeee9;display:flex;align-items:center;justify-content:center;cursor:move;"></div>',
              iconSize: [14, 14],
              iconAnchor: [7, 7]
            });
            permanentMarker.setIcon(hoverIcon);
          });
          permanentMarker.on('mouseout', () => {
            permanentMarker.setIcon(vertexIcon);
          });

          // Update rectangle when corner is dragged
          permanentMarker.on('drag', () => {
            const newLatLng = permanentMarker.getLatLng();
            const currentCorners = [
              permanentVertexMarkersRef.current[0].getLatLng(),
              permanentVertexMarkersRef.current[1].getLatLng(),
              permanentVertexMarkersRef.current[2].getLatLng(),
              permanentVertexMarkersRef.current[3].getLatLng()
            ];
            currentCorners[index] = newLatLng;
            
            // Update rectangle bounds based on new corner positions
            const newBounds = L.latLngBounds(currentCorners);
            finalRect.setBounds(newBounds);
            
            // Update all corner markers to match new bounds
            const updatedCorners = [
              newBounds.getNorthWest(),
              newBounds.getNorthEast(),
              newBounds.getSouthEast(),
              newBounds.getSouthWest()
            ];
            permanentVertexMarkersRef.current.forEach((marker, i) => {
              marker.setLatLng(updatedCorners[i]);
            });
          });

          // Update state when drag ends
          permanentMarker.on('dragend', () => {
            const updatedBounds = finalRect.getBounds();
            const center = updatedBounds.getCenter();
            setAoiCoords(`${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`);
            setAoiState(prev => ({
              ...prev,
              currentAOI: {
                polygon: JSON.stringify(finalRect.toGeoJSON().geometry),
                area: 0,
                bounds: {
                  north: updatedBounds.getNorth(),
                  south: updatedBounds.getSouth(),
                  east: updatedBounds.getEast(),
                  west: updatedBounds.getWest(),
                }
              }
            }));
            toast.success('Vertex position updated');
          });

          permanentVertexMarkersRef.current.push(permanentMarker);
        });

        // Compute center and save state
        const center = bounds.getCenter();
        setAoiCoords(`${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`);
        setAoiState(prev => ({
          ...prev,
          currentAOI: {
            polygon: JSON.stringify(finalRect.toGeoJSON().geometry),
            area: 0,
            bounds: {
              north: bounds.getNorth(),
              south: bounds.getSouth(),
              east: bounds.getEast(),
              west: bounds.getWest(),
            }
          },
          isDrawing: false,
          drawingMode: null
        }));

        cleanupRectangleDraft(map);
        setActiveDrawingMode(null);
        // @ts-ignore
        map.pm.disableDraw?.();
        toast.success('Rectangle completed');
      };

      map.on('mousedown', onMouseDown);
      map.on('mousemove', onMouseMove);
      map.on('mouseup', onMouseUp);
      rectMouseDownRef.current = onMouseDown;
      rectMouseMoveRef.current = onMouseMove;
      rectMouseUpRef.current = onMouseUp;
    }

    setActiveDrawingMode(mode);
    setAoiState(prev => ({ ...prev, isDrawing: true, drawingMode: mode }));
    toast.info(`${mode} drawing mode activated`, {
      description: 'Click on the map to start drawing'
    });
  };

  // Clear drawing
  const clearDrawing = () => {
    if (drawingLayerRef.current) {
      drawingLayerRef.current.clearLayers();
      currentPolygonRef.current = null;
      
      // Clear permanent vertex markers
      permanentVertexMarkersRef.current.forEach(m => m.remove());
      permanentVertexMarkersRef.current = [];
      
      setAoiArea('No area defined');
      setAoiCoords('None');
      setAoiState(prev => ({ ...prev, currentAOI: undefined }));
      toast.success('Drawing cleared');
    }
    if (mapInstanceRef.current && activeDrawingMode) {
      mapInstanceRef.current.pm.disableDraw();
      setActiveDrawingMode(null);
    }
  };

  // Handle file upload
  const handleFileUpload = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    
    // Create mock tree structure
    const mockTreeData: TreeNode[] = [
      {
        id: 'network-design-root',
        label: file.name.replace(/\.[^/.]+$/, ""),
        children: [
          {
            id: 'poles',
            label: 'Poles',
            children: [
              { id: 'poles-3rd-party', label: '3rd Party Poles' },
              { id: 'poles-ex-client', label: 'EX Client Poles' },
              { id: 'poles-new-client', label: 'New Client Poles' }
            ]
          },
          {
            id: 'landmarks',
            label: 'Landmarks',
            children: [
              { id: 'landmarks-buildings', label: 'Buildings Polygons' },
              { id: 'landmarks-roads', label: 'Traced Roads' },
              { id: 'landmarks-places', label: 'Place Names' }
            ]
          }
        ]
      }
    ];

    setUploadedDesign({
      file,
      layers: mockTreeData,
      processed: true
    });

    setDesignAccordionOpen(true);

    logActivity({
      action: 'upload_design',
      appId: 'features',
      appName: 'Features',
      description: `Uploaded design file: ${file.name}`,
      data: { filename: file.name, size: file.size }
    });

    toast.success('Design uploaded', {
      description: file.name
    });
  }, [logActivity]);

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    handleFileUpload(e.dataTransfer.files);
  };

  // Run analysis
  const runAnalysis = async () => {
    if (!aoiState.currentAOI) {
      toast.error('No area defined', {
        description: 'Please draw an area on the map first'
      });
      return;
    }

    const newJobStatus = {
      id: 'job-' + Date.now(),
      status: 'processing' as const,
      progress: 0,
      message: 'Starting extraction...'
    };
    setJobStatus(newJobStatus);

    toast.loading('Starting extraction...', { id: 'extraction' });

    await logActivity({
      action: 'start_extraction',
      appId: 'features',
      appName: 'Features',
      description: 'Started feature extraction job',
      data: { 
        jobId: newJobStatus.id,
        aoi: aoiState.currentAOI,
        sources: Object.entries(dataSources).filter(([_, enabled]) => enabled).map(([name]) => name)
      }
    });

    // Simulate progress
    setTimeout(() => {
      setJobStatus(prev => prev ? { ...prev, progress: 50, message: 'Extracting buildings...' } : null);
      toast.loading('Extracting buildings...', { id: 'extraction' });
    }, 2000);

    setTimeout(async () => {
      const completedStatus = { 
        id: newJobStatus.id,
        status: 'completed' as const, 
        progress: 100, 
        message: 'Extraction completed' 
      };
      setJobStatus(completedStatus);
      toast.success('Extraction completed', { id: 'extraction' });

      await logActivity({
        action: 'extraction_completed',
        appId: 'features',
        appName: 'Features',
        description: 'Feature extraction completed successfully'
      });
    }, 4000);
  };

  const toggleDataSource = (sourceName: string) => {
    setDataSources(prev => ({
      ...prev,
      [sourceName]: !prev[sourceName]
    }));
  };

  // Change map layer
  const changeMapLayer = (mapType: keyof typeof mapSources, provider: string) => {
    if (!mapInstanceRef.current || !currentTileLayerRef.current) return;

    const map = mapInstanceRef.current;
    const sources = mapSources[mapType] as any;
    const newSource = sources[provider];

    if (newSource) {
      // Remove current layer
      currentTileLayerRef.current.remove();

      // Add new layer
      const newTileLayer = L.tileLayer(newSource.url, {
        attribution: newSource.attribution,
        maxZoom: 19
      });

      newTileLayer.addTo(map);
      currentTileLayerRef.current = newTileLayer;

      setCurrentMapType(mapType);
      setCurrentProvider(provider);
      setShowLayerSelector(false);
      
      toast.success(`Map changed to ${newSource.name}`);
    }
  };

  // Close layer selector when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showLayerSelector) {
        const target = event.target as Element;
        if (!target.closest('.layer-selector-container')) {
          setShowLayerSelector(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showLayerSelector]);

  return (
    <div className="flex h-screen bg-[#062226]">
      {/* Content Panel - Following vanilla layout */}
      <div className="w-[400px] bg-[#062226] p-6 overflow-y-auto flex flex-col gap-6">
        {/* Design Upload Accordion */}
        <div className="bg-[#132f35] border border-[rgba(255,255,255,0.1)] rounded-[5px] p-8">
          <button
            onClick={() => setDesignAccordionOpen(!designAccordionOpen)}
            className="w-full flex items-center justify-between text-white text-sm font-medium mb-4"
          >
            <span>Upload Design</span>
            {designAccordionOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {designAccordionOpen && (
            <div className="space-y-4">
              {!uploadedDesign ? (
                <>
                  <input
                    type="file"
                    id="design-file"
                    accept=".geojson,.json,.kml,.kmz"
                    className="hidden"
                    onChange={(e) => handleFileUpload(e.target.files)}
                  />
                  <div
                    className="border-2 border-dashed border-[rgba(255,255,255,0.1)] rounded-[5px] p-8 text-center cursor-pointer hover:border-[#0e5a81] hover:bg-[rgba(14,90,129,0.1)] transition-all"
                    onClick={() => document.getElementById('design-file')?.click()}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                  >
                    <UploadIcon className="w-8 h-8 text-[#0e5a81] mx-auto mb-2" />
                    <p className="text-[#b0c4c8] text-sm">Drop HLD file or click to browse</p>
                    <p className="text-[#b0c4c8] text-xs mt-1">Supported: KMZ, KML, GeoJSON</p>
                  </div>
                </>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-[#059669] bg-opacity-20 border border-[#059669] border-opacity-30 rounded-[5px]">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <CheckCircle2 className="w-5 h-5 text-[#059669] flex-shrink-0" />
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-white" />
                          <span className="text-sm text-white truncate">{uploadedDesign.file.name}</span>
                        </div>
                        <p className="text-xs text-[#b0c4c8]">
                          {(uploadedDesign.file.size / 1024 / 1024).toFixed(2)} MB • Processed
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setUploadedDesign(null)}
                      className="p-1 hover:bg-red-500 hover:bg-opacity-20 rounded transition-colors"
                    >
                      <X className="w-4 h-4 text-[#b0c4c8] hover:text-red-500" />
                    </button>
                  </div>

                  {uploadedDesign.layers.length > 0 && (
                    <div>
                      <label className="text-xs font-medium text-[#b0c4c8] mb-2 block">Design Layers</label>
                      <div className="max-h-64 overflow-y-auto bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.1)] rounded-[5px] p-2">
                        <TreeView
                          data={uploadedDesign.layers}
                          onNodeClick={(node) => console.log('Layer clicked:', node.id)}
                          defaultExpandedIds={[uploadedDesign.layers[0]?.id]}
                          showLines={true}
                          animateExpand={true}
                          indent={16}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* AOI Accordion */}
        <div className="bg-[#132f35] border border-[rgba(255,255,255,0.1)] rounded-[5px] p-8">
          <button
            onClick={() => setAoiAccordionOpen(!aoiAccordionOpen)}
            className="w-full flex items-center justify-between text-white text-sm font-medium mb-4"
          >
            <span>Area of Interest</span>
            {aoiAccordionOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {aoiAccordionOpen && (
            <div className="space-y-4">
              <div className="space-y-3">
                <div className="flex flex-col gap-1">
                  <span className="text-[#b0c4c8] text-xs">Area:</span>
                  <span className="text-white text-sm">{aoiArea}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[#b0c4c8] text-xs">Coordinates:</span>
                  <span className="text-white text-sm break-all">{aoiCoords}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Data Sources */}
        <div className="bg-[#132f35] border border-[rgba(255,255,255,0.1)] rounded-[5px] p-8">
          <h3 className="text-white text-sm font-medium mb-4">Data Sources</h3>
          <div className="space-y-2">
            {Object.entries(dataSources).map(([key, enabled]) => (
              <label key={key} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={() => toggleDataSource(key)}
                  className="w-4 h-4 rounded border-[rgba(255,255,255,0.1)] bg-[#132f35] text-[#0e5a81]"
                />
                <span className="text-sm text-white capitalize">{key.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="bg-[#132f35] border border-[rgba(255,255,255,0.1)] rounded-[5px] p-8">
          <h3 className="text-white text-sm font-medium mb-4">Run Analysis</h3>
          
          {jobStatus && (
            <div className="mb-4 p-3 bg-[#1f3539] border border-[rgba(255,255,255,0.1)] rounded-[5px]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-white">Processing</span>
                <span className="text-xs text-[#b0c4c8]">{jobStatus.progress}%</span>
              </div>
              <div className="w-full bg-[#062226] rounded-full h-1.5 mb-2">
                <div 
                  className="bg-[#0e5a81] h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${jobStatus.progress}%` }}
                ></div>
              </div>
              <p className="text-xs text-[#b0c4c8]">{jobStatus.message}</p>
            </div>
          )}

          <div className="flex justify-end gap-3">
            <button
              onClick={clearDrawing}
              className="px-4 py-2 text-sm text-[#b0c4c8] hover:text-white transition-colors"
            >
              Clear
            </button>
            <button
              onClick={runAnalysis}
              disabled={!aoiState.currentAOI || jobStatus?.status === 'processing'}
              className="flex items-center gap-2 px-4 py-2 bg-[#0e5a81] text-white text-sm font-medium rounded-md hover:bg-[#0a4d6b] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" />
              Run
            </button>
          </div>
        </div>
      </div>

      {/* Map Panel */}
      <div className="flex-1 relative bg-[#132f35] rounded-[5px] m-6 ml-0 overflow-hidden">
        {/* Drawing Controls - Top Left */}
        <div className="absolute top-6 left-6 z-[1000] flex gap-1 bg-white/95 rounded-lg p-1.5 shadow-lg">
          <button
            onClick={() => enableDrawing('polygon')}
            disabled={!!aoiState.currentAOI}
            className={`p-2 rounded transition-colors ${
              aoiState.currentAOI
                ? 'opacity-40 cursor-not-allowed text-gray-400'
                : activeDrawingMode === 'polygon'
                ? 'bg-blue-100 text-blue-700'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
            title={aoiState.currentAOI ? 'Clear existing shape first' : 'Draw Polygon'}
          >
            <Pentagon className="w-5 h-5" />
          </button>
          <button
            onClick={() => enableDrawing('rectangle')}
            disabled={!!aoiState.currentAOI}
            className={`p-2 rounded transition-colors ${
              aoiState.currentAOI
                ? 'opacity-40 cursor-not-allowed text-gray-400'
                : activeDrawingMode === 'rectangle'
                ? 'bg-blue-100 text-blue-700'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
            title={aoiState.currentAOI ? 'Clear existing shape first' : 'Draw Rectangle'}
          >
            <Square className="w-5 h-5" />
          </button>
          <button
            onClick={clearDrawing}
            disabled={!aoiState.currentAOI}
            className={`p-2 rounded transition-colors ${
              aoiState.currentAOI
                ? 'hover:bg-red-50 hover:text-red-600 text-gray-700'
                : 'opacity-40 cursor-not-allowed text-gray-400'
            }`}
            title={aoiState.currentAOI ? 'Clear Drawing' : 'No shape to clear'}
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>

        {/* Map Layer Selector - Top Right */}
        <div className="absolute top-6 right-6 z-[1000] layer-selector-container">
          <button
            onClick={() => setShowLayerSelector(!showLayerSelector)}
            className="p-2 bg-white/95 rounded-lg shadow-lg hover:bg-white transition-colors"
            title="Change Map Layer"
          >
            <Layers className="w-5 h-5 text-gray-700" />
          </button>

          {/* Layer Selector Dropdown */}
          {showLayerSelector && (
            <div className="absolute top-full right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg min-w-[200px] overflow-hidden">
              {Object.entries(mapSources).map(([mapType, providers]) => (
                <div key={mapType}>
                  <div className="px-3 py-2 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    {mapType}
                  </div>
                  {Object.entries(providers).map(([provider, config]) => (
                    <button
                      key={provider}
                      onClick={() => changeMapLayer(mapType as keyof typeof mapSources, provider)}
                      className={`w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
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

        {/* Map Container */}
        <div ref={mapRef} className="w-full h-full" />
      </div>
    </div>
  );
}
