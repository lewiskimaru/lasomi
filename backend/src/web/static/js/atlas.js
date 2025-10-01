/**
 * Atlas API Web Interface JavaScript
 */

class AtlasomiInterface {
    constructor() {
        this.map = null;
        this.currentPolygon = null;
        this.currentMarker = null;
        this.currentShapeType = null;
        this.drawingLayer = null;
        this.dataLayers = new Map();
        this.designLayers = new Map(); // Track individual design layers
        this.designLayerGroup = null; // Layer group for all design layers
        this.currentJobId = null;
        this.apiBaseUrl = '/api/v2';  // Fixed the API base URL
        this.settings = null;
        this.mapSources = this.initializeMapSources();
        this.userMapPreferences = this.loadMapPreferences();
        
        this.init();
    }

    init() {
        this.initMap();
        this.setupEventListeners();
        this.setupDrawingControls();
    }

    initMap() {
        this.map = L.map('map', { zoomControl: false }).setView([-1.2921, 36.8219], 13);
        this.addTileLayer('satellite');
        this.drawingLayer = L.layerGroup().addTo(this.map);

        // Initialize design layer group (featureGroup provides getBounds())
        this.designLayerGroup = L.featureGroup().addTo(this.map);

        // Add custom attribution
        this.addCustomAttribution();
    }

    setupEventListeners() {
        // Map controls - updated for new layout
        // Map type selector
        const mapTypeSelector = document.getElementById('map-type-selector');
        if (mapTypeSelector) {
            mapTypeSelector.addEventListener('change', (e) => {
                this.changeMapType(e.target.value);
            });
        }

        // Zoom controls
        const zoomIn = document.getElementById('zoom-in');
        const zoomOut = document.getElementById('zoom-out');
        if (zoomIn) {
            zoomIn.addEventListener('click', () => this.map.zoomIn());
        }
        if (zoomOut) {
            zoomOut.addEventListener('click', () => this.map.zoomOut());
        }

        // Drawing controls - with null checking
        const drawPolygon = document.getElementById('draw-polygon');
        const drawRectangle = document.getElementById('draw-rectangle');
        const drawMarker = document.getElementById('draw-marker');
        const deleteShape = document.getElementById('delete-shape');

        if (drawPolygon) {
            drawPolygon.addEventListener('click', () => this.enablePolygonDrawing());
        }
        if (drawRectangle) {
            drawRectangle.addEventListener('click', () => this.enableRectangleDrawing());
        }
        if (drawMarker) {
            drawMarker.addEventListener('click', () => this.enableMarkerDrawing());
        }
        if (deleteShape) {
            deleteShape.addEventListener('click', () => this.deleteCurrentShape());
        }
        const globalSearch = document.getElementById('global-search');
        if (globalSearch) {
            globalSearch.addEventListener('input', this.debounce((e) => {
                this.performProgressiveSearch(e.target.value);
            }, 300));
            
            globalSearch.addEventListener('focus', (e) => {
                if (e.target.value.trim()) {
                    this.performProgressiveSearch(e.target.value);
                }
            });
            
            globalSearch.addEventListener('blur', () => {
                // Hide suggestions after a short delay to allow clicking on suggestions
                setTimeout(() => {
                    this.hideSearchSuggestions();
                }, 200);
            });
        }

        // Settings button
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.openSettingsModal());
        }

        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearDrawing());
        }

        // File upload - moved the upload button logic to setupFileUpload
        this.setupFileUpload();

        // Actions
        const runBtn = document.getElementById('run-btn');
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runAnalysis());
        }

        // Download button
        const downloadBtn = document.getElementById('download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadResults());
        }

        // Settings modal
        const settingsCancel = document.getElementById('settings-cancel');
        const settingsApply = document.getElementById('settings-apply');

        if (settingsCancel) {
            settingsCancel.addEventListener('click', () => this.closeSettingsModal());
        }
        if (settingsApply) {
            settingsApply.addEventListener('click', () => this.applySettings());
        }

        // Export modal
        const cancelExport = document.getElementById('cancel-export');
        if (cancelExport) {
            cancelExport.addEventListener('click', () => this.hideExportModal());
        }
        const confirmExport = document.getElementById('confirm-export');
        if (confirmExport) {
            confirmExport.addEventListener('click', () => this.performExport());
        }

        // Response toggle
        const responseToggle = document.getElementById('response-toggle');
        if (responseToggle) {
            responseToggle.addEventListener('click', () => this.toggleResponse());
        }

        // Results toggle
        const resultsToggle = document.getElementById('results-toggle');
        if (resultsToggle) {
            resultsToggle.addEventListener('click', () => this.toggleResults());
        }

        // Layer toggle (if still present)
        const layerToggle = document.getElementById('layer-toggle');
        if (layerToggle) {
            layerToggle.addEventListener('click', () => this.toggleLayerPanel());
        }

        // Sidebar navigation
        document.querySelectorAll('.sidebar-nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (item.getAttribute('href') === '#') {
                    e.preventDefault();
                    this.switchTab(item.dataset.tab);
                }
            });
        });

        // Add accordion event listeners
        this.setupAccordionListeners();
        
        // Setup layer cycling control
        this.setupLayerCycling();
    }

    // Add method to set up accordion functionality
    setupAccordionListeners() {
        // AOI accordion toggle
        const aoiToggle = document.getElementById('aoi-toggle');
        if (aoiToggle) {
            aoiToggle.addEventListener('click', () => this.toggleAccordion('aoi'));
        }

        // Design accordion toggle
        const designToggle = document.getElementById('design-toggle');
        if (designToggle) {
            designToggle.addEventListener('click', () => this.toggleAccordion('design'));
        }
    }

    // Toggle accordion sections
    toggleAccordion(type) {
        const toggle = document.getElementById(`${type}-toggle`);
        const content = document.getElementById(`${type}-content`);
        const icon = toggle?.querySelector('i');
        
        if (toggle && content && icon) {
            const isExpanded = toggle.classList.contains('expanded');
            
            if (isExpanded) {
                // Collapse
                toggle.classList.remove('expanded');
                content.style.display = 'none';
                icon.className = 'fas fa-chevron-down';
            } else {
                // Expand
                toggle.classList.add('expanded');
                content.style.display = 'block';
                icon.className = 'fas fa-chevron-up';
            }
        }
    }

    setupDrawingControls() {
        this.currentDrawMode = 'marker';
        this.isDrawingActive = false;
        this.currentMarker = null;

        // Check if Leaflet.draw is available
        if (typeof L.Draw === 'undefined') {
            console.error('Leaflet.draw library not loaded. Drawing functionality will be limited.');
            this.setupBasicDrawing();
            return;
        }

        try {
            // Initialize Leaflet Draw for polygon and rectangle modes
            this.drawControl = new L.Control.Draw({
                draw: {
                    polygon: {
                        shapeOptions: {
                            color: '#2563eb',
                            weight: 3,
                            fillOpacity: 0.1
                        },
                        allowIntersection: false,
                        showArea: true
                    },
                    rectangle: {
                        shapeOptions: {
                            color: '#2563eb',
                            weight: 3,
                            fillOpacity: 0.1
                        },
                        showArea: true
                    },
                    polyline: false,
                    circle: false,
                    marker: true,
                    circlemarker: false
                },
                edit: {
                    featureGroup: this.drawingLayer,
                    remove: true,
                    edit: {
                        selectedPathOptions: {
                            maintainColor: true,
                            opacity: 0.6,
                            dashArray: '10, 10',
                            fillOpacity: 0.1
                        }
                    }
                }
            });

            // Store references to drawing handlers
            this.polygonDrawer = new L.Draw.Polygon(this.map, this.drawControl.options.draw.polygon);
            this.rectangleDrawer = new L.Draw.Rectangle(this.map, this.drawControl.options.draw.rectangle);
            this.markerDrawer = new L.Draw.Marker(this.map, this.drawControl.options.draw.marker);

            // Set up event listeners
            this.map.on(L.Draw.Event.CREATED, (e) => this.onShapeDrawn(e.layer, e.layerType));
            this.map.on(L.Draw.Event.DELETED, () => this.onShapeDeleted());
            this.map.on(L.Draw.Event.EDITED, (e) => this.onShapeEdited(e.layers));

            console.log('Leaflet.draw initialized successfully');
        } catch (error) {
            console.error('Error initializing Leaflet.draw:', error);
            this.setupBasicDrawing();
        }

        // Add click handler for marker placement mode
        this.map.on('click', (e) => this.onMapClick(e));
    }

    setupBasicDrawing() {
        console.log('Setting up basic drawing functionality as fallback');
        // This provides basic drawing functionality if Leaflet.draw fails
        this.basicDrawingMode = true;

        // For basic drawing, we'll handle polygon creation manually
        this.polygonPoints = [];
        this.isDrawingPolygon = false;
        this.tempPolygonLayer = null;
    }

    setupFileUpload() {
        // Get DOM elements with null checking
        const uploadBtn = document.getElementById('upload-btn');
        const fileInput = document.getElementById('design-file');

        console.log('Setting up file upload functionality');
        console.log('Upload button found:', !!uploadBtn);
        console.log('File input found:', !!fileInput);

        // Check if required elements exist
        if (!fileInput) {
            console.warn('File input element (design-file) not found. File upload functionality will be disabled.');
            return;
        }

        if (!uploadBtn) {
            console.warn('Upload button element (upload-btn) not found. Upload button functionality will be disabled.');
            return;
        }

        // Remove any existing event listeners to prevent duplicates
        uploadBtn.removeEventListener('click', this._uploadBtnHandler);
        
        // Store handler for potential removal
        this._uploadBtnHandler = (e) => {
            console.log('Upload button clicked');
            e.preventDefault();
            e.stopPropagation(); // Prevent accordion toggle
            fileInput.click();
        };

        // Set up upload button click handler
        uploadBtn.addEventListener('click', this._uploadBtnHandler);

        // Set up file input change handler
        fileInput.addEventListener('change', (e) => {
            console.log('File selected:', e.target.files);
            if (e.target.files.length > 0) {
                this.handleDesignUpload(e.target.files[0]);
            }
        });

        // Set up drag and drop on the entire AOI card for better UX
        const aoiCard = document.querySelector('.aoi-card');
        if (aoiCard) {
            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                aoiCard.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });

            // Highlight drop area
            ['dragenter', 'dragover'].forEach(eventName => {
                aoiCard.addEventListener(eventName, () => {
                    aoiCard.classList.add('drag-highlight');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                aoiCard.addEventListener(eventName, () => {
                    aoiCard.classList.remove('drag-highlight');
                }, false);
            });

            // Handle dropped files
            aoiCard.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                console.log('Files dropped:', files);
                if (files.length > 0) {
                    this.handleDesignUpload(files[0]);
                }
            }, false);
        } else {
            console.warn('AOI card element not found. Drag and drop functionality will be disabled.');
        }
    }

    async handleDesignUpload(file) {
        console.log('Handling design upload for file:', file);
        try {
            // Toast: show non-blocking loading
            if (window.Toast) {
                window.Toast.loading({ id: 'upload', title: 'Processing design', message: file?.name || '' });
            }
            // Overlay removed: rely on toast notifications only
            
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('file', file);
            
            // Upload file to backend - Fixed the endpoint URL
            const response = await fetch('/api/v2/designs/upload', {
                method: 'POST',
                body: formData
            });
            
            console.log('Upload response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Upload result:', result);
            
            // Hide loading overlay
            this.hideLoadingOverlay();
            
            // Show success notification
            if (window.Toast) {
                window.Toast.success({ id: 'upload', title: 'Design processed', message: 'Layers rendered on the map' });
            }
            this.showNotification(result.message, 'success');
            
            // Render the design on the map
            await this.renderDesignOnMap(result.design_id);
            
            // Navigate map to design area
            this.map.fitBounds([
                [result.map_bounds[1], result.map_bounds[0]], 
                [result.map_bounds[3], result.map_bounds[2]]
            ]);
            
            // Show layer information in UI
            this.displayDesignLayers(result.layer_summary);
            
            // Update design accordion with file info
            this.updateDesignAccordion(file.name, result.layer_summary);
            
            // Expand the design accordion
            const designToggle = document.getElementById('design-toggle');
            if (designToggle && !designToggle.classList.contains('expanded')) {
                this.toggleAccordion('design');
            }
            
        } catch (error) {
            console.error('Design upload error:', error);
            this.hideLoadingOverlay();
            if (window.Toast) {
                window.Toast.error({ id: 'upload', title: 'Upload failed', message: error.message });
            }
            this.showNotification(`Error uploading design: ${error.message}`, 'error');
        }
    }

    async renderDesignOnMap(designId) {
        try {
            console.log('Rendering design with ID:', designId);
            
            // Request design rendering from backend
            const response = await fetch('/api/v2/designs/render', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ design_id: designId })
            });
            
            if (!response.ok) {
                throw new Error(`Rendering failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Design render result:', result);
            
            // Clear any existing design layers
            this.clearDesignLayers();
            
            // Ensure design layer group exists
            if (!this.designLayerGroup) {
                this.designLayerGroup = L.layerGroup().addTo(this.map);
            }
            
            // Check if we have layers to render
            if (!result.layers || result.layers.length === 0) {
                console.warn('No layers found in design render result');
                this.showNotification('No layers found in design file', 'warning');
                return;
            }
            
            // Define color palette for layers
            const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#e67e22', '#8e44ad', '#2c3e50'];
            
            // Add each layer to the map with unique styling
            result.layers.forEach((layerData, index) => {
                try {
                    // Handle different possible data structures
                    let featureCollection = null;
                    let featureCount = 0;
                    
                    // Check various possible structures
                    if (layerData.features) {
                        featureCollection = layerData.features;
                        featureCount = layerData.features.features?.length || 0;
                    } else if (layerData.geojson) {
                        featureCollection = layerData.geojson;
                        featureCount = layerData.geojson.features?.length || 0;
                    } else if (layerData.feature_count && layerData.feature_count > 0) {
                        // Layer has features but structure is different, log for debugging
                        console.warn(`Layer ${layerData.name} reports ${layerData.feature_count} features but no accessible feature data`);
                        console.log('Layer data structure:', Object.keys(layerData));
                        console.log('Full layer data:', layerData);
                    }
                    
                    console.log(`Processing layer ${index}:`, layerData.name, 'with', featureCount, 'features');
                    console.log('Feature collection:', featureCollection);
                    
                    if (!featureCollection || !featureCollection.features || featureCollection.features.length === 0) {
                        console.warn(`Layer ${layerData.name} has no accessible features, skipping`);
                        return;
                    }
                    
                    const colorIndex = index % colors.length;
                    const layerColor = colors[colorIndex];
                    
                    const geojsonLayer = L.geoJSON(featureCollection, {
                        style: (feature) => {
                            return {
                                color: layerColor,
                                weight: 2,
                                fillOpacity: 0.4,
                                fillColor: layerColor,
                                opacity: 0.8
                            };
                        },
                        pointToLayer: (feature, latlng) => {
                            // Use circle markers instead of default map pin icons
                            return L.circleMarker(latlng, {
                                radius: 6, // Appropriate diameter for readability
                                color: layerColor,
                                weight: 2,
                                fillOpacity: 0.7,
                                fillColor: layerColor,
                                opacity: 1
                            });
                        },
                        onEachFeature: (feature, leafletLayer) => {
                            if (feature.properties) {
                                let popupContent = `<div class="popup-content"><strong>Layer:</strong> ${layerData.name}<br>`;
                                Object.entries(feature.properties).forEach(([key, value]) => {
                                    if (value !== null && value !== undefined && value !== '') {
                                        popupContent += `<strong>${key}:</strong> ${value}<br>`;
                                    }
                                });
                                popupContent += '</div>';
                                leafletLayer.bindPopup(popupContent);
                            }
                        }
                    });
                    
                    // Store individual design layers for toggling
                    this.designLayers.set(layerData.name, geojsonLayer);
                    
                    // Add to design layer group
                    this.designLayerGroup.addLayer(geojsonLayer);
                    
                    console.log(`Successfully added layer: ${layerData.name}`);
                    
                } catch (layerError) {
                    console.error(`Error processing layer ${layerData.name}:`, layerError);
                }
            });
            
            // Fit map to design bounds if layers were added
            if (this.designLayers.size > 0) {
                try {
                    this.map.fitBounds(this.designLayerGroup.getBounds(), { padding: [20, 20] });
                } catch (boundsError) {
                    console.warn('Could not fit bounds to design layers:', boundsError);
                }
            }
            
            console.log(`Design rendering complete. Added ${this.designLayers.size} layers.`);
            this.showNotification(`Design rendered successfully with ${this.designLayers.size} layers`, 'success');
            
        } catch (error) {
            console.error('Design rendering error:', error);
            this.showNotification(`Error rendering design: ${error.message}`, 'error');
            
            // Fallback: try to render with basic styling
            this.renderDesignFallback(designId);
        }
    }

    clearDesignLayers() {
        // Clear all design layers from the layer group
        if (this.designLayerGroup) {
            this.designLayerGroup.clearLayers();
        }
        
        // Clear the design layers map
        this.designLayers.clear();
        
        console.log('Design layers cleared');
    }

    async renderDesignFallback(designId) {
        try {
            console.log('Attempting fallback rendering for design:', designId);
            
            // Try to get the raw design data and render with basic styling
            const response = await fetch('/api/v2/designs/render', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ design_id: designId, fallback: true })
            });
            
            if (!response.ok) {
                throw new Error(`Fallback rendering failed: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.geojson) {
                // Render entire design as single layer with base color
                const fallbackLayer = L.geoJSON(result.geojson, {
                    style: {
                        color: '#3498db',
                        weight: 2,
                        fillOpacity: 0.3,
                        fillColor: '#3498db'
                    },
                    pointToLayer: (feature, latlng) => {
                        // Use circle markers for fallback rendering too
                        return L.circleMarker(latlng, {
                            radius: 6,
                            color: '#3498db',
                            weight: 2,
                            fillOpacity: 0.7,
                            fillColor: '#3498db',
                            opacity: 1
                        });
                    },
                    onEachFeature: (feature, layer) => {
                        if (feature.properties) {
                            let popupContent = '<div class="popup-content"><strong>Design Feature</strong><br>';
                            Object.entries(feature.properties).forEach(([key, value]) => {
                                if (value !== null && value !== undefined && value !== '') {
                                    popupContent += `<strong>${key}:</strong> ${value}<br>`;
                                }
                            });
                            popupContent += '</div>';
                            layer.bindPopup(popupContent);
                        }
                    }
                });
                
                // Store as single design layer
                this.designLayers.set('Design', fallbackLayer);
                this.designLayerGroup.addLayer(fallbackLayer);
                
                // Fit map to bounds
                try {
                    this.map.fitBounds(this.designLayerGroup.getBounds(), { padding: [20, 20] });
                } catch (boundsError) {
                    console.warn('Could not fit bounds to fallback design:', boundsError);
                }
                
                this.showNotification('Design rendered with basic styling', 'info');
                console.log('Fallback rendering successful');
            }
            
        } catch (error) {
            console.error('Fallback rendering failed:', error);
            this.showNotification('Failed to render design file', 'error');
        }
    }

    displayDesignLayers(layerSummary) {
        // Create or update layer controls for design layers
        const layerToggles = document.getElementById('layer-toggles');
        if (!layerToggles) return;
        
        // Clear existing design layer toggles
        const existingDesignToggles = layerToggles.querySelectorAll('[data-design-layer]');
        existingDesignToggles.forEach(toggle => toggle.remove());
        
        // Add design layer toggles
        layerSummary.forEach(layer => {
            const toggle = document.createElement('div');
            toggle.className = 'layer-toggle';
            toggle.dataset.designLayer = layer.name;
            
            // Check if layer is currently visible
            const designLayer = this.designLayers.get(layer.name);
            const isVisible = designLayer && this.designLayerGroup && this.designLayerGroup.hasLayer(designLayer);
            
            toggle.innerHTML = `
                <div class="layer-toggle-info">
                    <div class="layer-name">${layer.name}</div>
                    <div class="layer-source">Design Layer (${layer.feature_count} features)</div>
                </div>
                <div class="layer-switch ${isVisible ? 'active' : ''}" data-design-layer="${layer.name}"></div>
            `;
            
            // Add click event to toggle layer visibility
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleDesignLayer(layer.name);
            });
            
            layerToggles.appendChild(toggle);
        });
    }

    toggleDesignLayer(layerName) {
        console.log('Toggling design layer:', layerName);
        const layer = this.designLayers.get(layerName);
        
        // Find both types of toggle switches
        const mainSwitchElement = document.querySelector(`[data-design-layer="${layerName}"].layer-switch`);
        const accordionToggleElement = document.querySelector(`[data-layer="${layerName}"].design-layer-toggle`);
        
        if (layer && this.designLayerGroup) {
            if (this.designLayerGroup.hasLayer(layer)) {
                this.designLayerGroup.removeLayer(layer);
                // Update both toggle switches
                if (mainSwitchElement) mainSwitchElement.classList.remove('active');
                if (accordionToggleElement) accordionToggleElement.classList.remove('active');
                console.log(`Removed layer: ${layerName}`);
            } else {
                this.designLayerGroup.addLayer(layer);
                // Update both toggle switches
                if (mainSwitchElement) mainSwitchElement.classList.add('active');
                if (accordionToggleElement) accordionToggleElement.classList.add('active');
                console.log(`Added layer: ${layerName}`);
            }
        } else {
            console.warn(`Layer not found or design layer group missing: ${layerName}`);
        }
    }

    // Update design accordion with uploaded file information
    updateDesignAccordion(filename, layerSummary) {
        // Update filename display
        const filenameElement = document.getElementById('design-filename');
        if (filenameElement) {
            filenameElement.textContent = filename;
        }

        // Populate layers section
        const layersContainer = document.getElementById('design-layers');
        if (layersContainer) {
            if (layerSummary && layerSummary.length > 0) {
                // Clear existing content
                layersContainer.innerHTML = '';
                
                // Add layer items
                layerSummary.forEach(layer => {
                    const layerItem = document.createElement('div');
                    layerItem.className = 'design-layer-item';
                    
                    // Check if layer is currently visible
                    const designLayer = this.designLayers.get(layer.name);
                    const isVisible = designLayer && this.designLayerGroup && this.designLayerGroup.hasLayer(designLayer);
                    
                    layerItem.innerHTML = `
                        <div class="design-layer-info">
                            <div class="design-layer-name">${layer.name}</div>
                            <div class="design-layer-stats">${layer.feature_count} features</div>
                        </div>
                        <div class="design-layer-toggle ${isVisible ? 'active' : ''}" data-layer="${layer.name}"></div>
                    `;
                    
                    // Add click event for layer toggle
                    const toggle = layerItem.querySelector('.design-layer-toggle');
                    toggle.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.toggleDesignLayer(layer.name);
                    });
                    
                    layersContainer.appendChild(layerItem);
                });
            } else {
                layersContainer.innerHTML = '<p class="empty-message">No layers found in design</p>';
            }
        }
    }

    // Update the existing handleFileUpload method to handle GeoJSON only
    async handleFileUpload(file) {
        // Check if it's a GeoJSON file
        if (file.name.endsWith('.geojson') || file.name.endsWith('.json')) {
            try {
                const text = await file.text();
                const geojson = JSON.parse(text);
                
                let geometry;
                if (geojson.type === 'FeatureCollection' && geojson.features.length > 0) {
                    geometry = geojson.features[0].geometry;
                } else if (geojson.type === 'Feature') {
                    geometry = geojson.geometry;
                } else if (geojson.type === 'Polygon') {
                    geometry = geojson;
                }
                
                if (geometry && geometry.type === 'Polygon') {
                    this.loadPolygonFromGeoJSON(geometry);
                    this.showNotification('GeoJSON loaded successfully', 'success');
                } else {
                    this.showNotification('Please upload a valid polygon geometry', 'error');
                }
            } catch (error) {
                console.error('GeoJSON parsing error:', error);
                this.showNotification('Error parsing GeoJSON file', 'error');
            }
        } else {
            // For other formats, use the new design upload handler
            this.handleDesignUpload(file);
        }
    }

    loadPolygonFromGeoJSON(geometry) {
        this.clearDrawing();
        const coordinates = geometry.coordinates[0].map(coord => [coord[1], coord[0]]);
        const polygon = L.polygon(coordinates, { color: '#2563eb', weight: 3, fillOpacity: 0.1 });
        this.drawingLayer.addLayer(polygon);
        this.currentPolygon = polygon;
        this.currentShapeType = 'polygon'; // Set as polygon for uploaded GeoJSON
        this.map.fitBounds(polygon.getBounds());
        this.updateAOIInfo();
        this.enableExtractButton();
    }

    changeMapType(type) {
        this.map.eachLayer((layer) => {
            if (layer instanceof L.TileLayer) this.map.removeLayer(layer);
        });
        this.addTileLayer(type);
        
        // Update layer cycling display when map type changes
        this.updateLayerCyclingDisplay();
    }

    addTileLayer(type) {
        // Get user's preferred source for this map type
        const userSource = this.userMapPreferences[type] || this.getDefaultSource(type);
        const sourceConfig = this.mapSources[type][userSource];
        
        // Fallback to default if user's preference is not available
        const layerConfig = sourceConfig || this.mapSources[type][this.getDefaultSource(type)];
        
        L.tileLayer(layerConfig.url, {
            attribution: layerConfig.attribution,
            subdomains: layerConfig.subdomains || ['a', 'b', 'c'],
            maxZoom: layerConfig.maxZoom || 18
        }).addTo(this.map);
    }

    addCustomAttribution() {
        // Add custom attribution to the existing attribution control
        // This preserves all existing attributions while adding our custom credit
        this.map.attributionControl.addAttribution('Built by <a href="https://linkedin.com/in/lewis-kimaru" target="_blank" rel="noopener">Lewis Kimaru</a>');
    }

    async performProgressiveSearch(query) {
        const trimmedQuery = query.trim();
        
        if (trimmedQuery.length < 2) {
            this.hideSearchSuggestions();
            return;
        }
        
        this.showSearchLoading();
        
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(trimmedQuery)}&limit=5&addressdetails=1`);
            const results = await response.json();
            
            if (results.length > 0) {
                this.displaySearchSuggestions(results);
            } else {
                this.showNoSearchResults();
            }
        } catch (error) {
            console.error('Search error:', error);
            this.hideSearchSuggestions();
        }
    }
    
    showSearchLoading() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        suggestionsContainer.innerHTML = '<div class="search-loading"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
        suggestionsContainer.classList.add('visible');
    }
    
    displaySearchSuggestions(results) {
        const suggestionsContainer = document.getElementById('search-suggestions');
        
        const suggestionsHTML = results.map(result => {
            const displayName = result.display_name.split(',').slice(0, 3).join(', ');
            const type = result.type || result.class || 'location';
            
            return `
                <div class="search-suggestion-item" data-lat="${result.lat}" data-lon="${result.lon}" data-name="${displayName}">
                    <i class="fas fa-map-marker-alt"></i>
                    <div class="search-suggestion-text">
                        <div>${displayName}</div>
                        <div class="search-suggestion-type">${type}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        suggestionsContainer.innerHTML = suggestionsHTML;
        suggestionsContainer.classList.add('visible');
        
        // Add click event listeners to suggestions
        suggestionsContainer.querySelectorAll('.search-suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const lat = parseFloat(item.dataset.lat);
                const lon = parseFloat(item.dataset.lon);
                const name = item.dataset.name;
                
                this.selectSearchResult(lat, lon, name);
            });
        });
    }
    
    showNoSearchResults() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        suggestionsContainer.innerHTML = '<div class="search-no-results">No locations found</div>';
        suggestionsContainer.classList.add('visible');
    }
    
    hideSearchSuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        suggestionsContainer.classList.remove('visible');
    }
    
    selectSearchResult(lat, lon, name) {
        // Center map on selected location
        this.map.setView([lat, lon], 15);
        
        // Update search input with selected name
        const globalSearch = document.getElementById('global-search');
        globalSearch.value = name;
        
        // Hide suggestions
        this.hideSearchSuggestions();
        
        // Add a temporary marker
        const marker = L.marker([lat, lon]).addTo(this.map)
            .bindPopup(`<strong>${name}</strong><br>Coordinates: ${lat.toFixed(4)}, ${lon.toFixed(4)}`)
            .openPopup();
        
        // Remove marker after 5 seconds
        setTimeout(() => {
            this.map.removeLayer(marker);
        }, 5000);
        
        this.showNotification('Location found', 'success');
    }

    searchByCoordinates() {
        const latInput = document.getElementById('lat-input');
        const lngInput = document.getElementById('lng-input');
        
        if (!latInput || !lngInput) {
            this.showNotification('Coordinate search not available in this view', 'info');
            return;
        }
        
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);

        if (!this.validateCoordinates(lat, lng)) {
            this.showNotification('Please enter valid coordinates (-90 to 90 for latitude, -180 to 180 for longitude)', 'error');
            return;
        }

        this.map.setView([lat, lng], 15);
        
        // Add a temporary marker
        const marker = L.marker([lat, lng]).addTo(this.map)
            .bindPopup(`Coordinates: ${lat.toFixed(4)}, ${lng.toFixed(4)}`)
            .openPopup();
        
        // Remove marker after 5 seconds
        setTimeout(() => {
            this.map.removeLayer(marker);
        }, 5000);
        
        this.showNotification('Location found', 'success');
    }

    enablePolygonDrawing() {
        this.disableAllDrawing();
        this.setActiveDrawTool('draw-polygon');
        this.currentDrawMode = 'polygon';
        this.isDrawingActive = true;

        // Try to enable Leaflet Draw polygon tool
        if (this.polygonDrawer) {
            try {
                this.polygonDrawer.enable();
                this.showNotification('Click on the map to start drawing a polygon', 'info');
            } catch (error) {
                console.error('Error enabling polygon drawer:', error);
                this.showNotification('Drawing tool error. Please try refreshing the page.', 'error');
            }
        } else if (this.basicDrawingMode) {
            // Fallback to basic drawing
            this.isDrawingPolygon = true;
            this.polygonPoints = [];
            this.showNotification('Click on the map to start drawing a polygon. Double-click to finish.', 'info');
        } else {
            this.showNotification('Drawing tools not available. Please refresh the page.', 'error');
        }
    }
    
    enableRectangleDrawing() {
        this.disableAllDrawing();
        this.setActiveDrawTool('draw-rectangle');
        this.currentDrawMode = 'rectangle';
        this.isDrawingActive = true;

        // Try to enable Leaflet Draw rectangle tool
        if (this.rectangleDrawer) {
            try {
                this.rectangleDrawer.enable();
                this.showNotification('Click and drag to draw a rectangle', 'info');
            } catch (error) {
                console.error('Error enabling rectangle drawer:', error);
                this.showNotification('Drawing tool error. Please try refreshing the page.', 'error');
            }
        } else {
            this.showNotification('Rectangle drawing not available. Please use polygon drawing instead.', 'warning');
        }
    }
    
    deleteCurrentShape() {
        if (this.currentPolygon || this.currentMarker) {
            this.clearDrawing();
            this.showNotification('Shape deleted', 'info');
        } else {
            this.showNotification('No shape to delete', 'warning');
        }
    }
    
    setActiveDrawTool(toolId) {
        // Remove active class from all draw buttons
        document.querySelectorAll('.draw-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to selected tool
        document.getElementById(toolId).classList.add('active');
    }
    
    enableVertexEditing() {
        if (this.currentPolygon && this.drawControl) {
            // Enable edit mode for the current shape
            this.drawControl._modes.edit.handler.enable();
            this.showNotification('Vertex editing enabled. Click and drag vertices to modify the shape.', 'info');
        } else {
            this.showNotification('No shape available to edit. Draw a shape first.', 'warning');
        }
    }

    enableMarkerDrawing() {
        this.disableAllDrawing();
        this.setActiveDrawTool('draw-marker');
        this.currentDrawMode = 'marker';
        this.isDrawingActive = true;
        this.showNotification('Click on the map to place a marker', 'info');
    }

    disableAllDrawing() {
        this.isDrawingActive = false;
        
        // Disable all drawing handlers
        if (this.polygonDrawer && this.polygonDrawer._enabled) {
            this.polygonDrawer.disable();
        }
        if (this.rectangleDrawer && this.rectangleDrawer._enabled) {
            this.rectangleDrawer.disable();
        }
        if (this.markerDrawer && this.markerDrawer._enabled) {
            this.markerDrawer.disable();
        }
    }

    onMapClick(e) {
        // Only handle clicks when in marker drawing mode
        if (this.currentDrawMode === 'marker' && this.isDrawingActive) {
            // Remove existing marker if any
            if (this.currentMarker) {
                this.drawingLayer.removeLayer(this.currentMarker);
            }
            
            // Create new marker
            this.currentMarker = L.marker(e.latlng, {
                draggable: true
            }).addTo(this.drawingLayer);
            
            // Add popup with coordinates
            const lat = e.latlng.lat.toFixed(6);
            const lng = e.latlng.lng.toFixed(6);
            this.currentMarker.bindPopup(`<strong>Coordinates:</strong><br>Lat: ${lat}<br>Lng: ${lng}`).openPopup();
            
            // Update coordinates display
            this.updateMarkerInfo(e.latlng);
            
            // Make marker draggable and update coordinates on drag
            this.currentMarker.on('dragend', (event) => {
                const marker = event.target;
                const position = marker.getLatLng();
                this.updateMarkerInfo(position);
                
                // Update popup
                const lat = position.lat.toFixed(6);
                const lng = position.lng.toFixed(6);
                marker.setPopupContent(`<strong>Coordinates:</strong><br>Lat: ${lat}<br>Lng: ${lng}`);
            });
            
            this.showNotification('Marker placed! Drag to adjust position.', 'success');
            
            // Enable run button
            document.getElementById('run-btn').disabled = false;
        }
    }

    clearDrawing() {
        this.drawingLayer.clearLayers();
        this.currentPolygon = null;
        this.currentMarker = null;
        this.currentShapeType = null;
        this.disableAllDrawing();
        this.updateAOIInfo();
        
        // Hide results card
        const resultsCard = document.getElementById('results-card');
        resultsCard.classList.remove('active');
        // Clear results
        this.dataLayers.forEach(layer => this.map.removeLayer(layer));
        this.dataLayers.clear();
        
        // Clear design layers but keep the group
        this.clearDesignLayers();
        
        // Reset results card to empty state
        document.getElementById('results-empty').style.display = 'block';
        document.getElementById('results-content').style.display = 'none';
        
        // Reset job ID
        this.currentJobId = null;
        
        // Disable download button
        document.getElementById('download-btn').disabled = true;
        
        // Reset to marker drawing mode
        this.setActiveDrawTool('draw-marker');
        this.currentDrawMode = 'marker';
    }

    onShapeDrawn(layer, layerType) {
        // Clear any existing shapes
        this.clearDrawing();
        
        // Add the new shape
        this.drawingLayer.addLayer(layer);
        this.currentPolygon = layer;
        this.currentShapeType = layerType;
        
        // Update AOI information
        this.updateAOIInfo();
        
        // Show success message
        const shapeTypeName = layerType === 'rectangle' ? 'rectangle' : 'polygon';
        this.showNotification(`${shapeTypeName.charAt(0).toUpperCase() + shapeTypeName.slice(1)} drawn successfully. You can now drag vertices to edit.`, 'success');
    }

    onShapeDeleted() {
        this.currentPolygon = null;
        this.currentShapeType = null;
        this.updateAOIInfo();
        this.showNotification('Shape deleted', 'info');
    }
    
    onShapeEdited(layers) {
        // Update the current polygon reference if it was edited
        layers.eachLayer((layer) => {
            if (layer === this.currentPolygon) {
                this.updateAOIInfo();
                this.showNotification('Shape updated', 'success');
            }
        });
    }

    updateMarkerInfo(latlng) {
        const areaElement = document.getElementById('aoi-area');
        const coordsElement = document.getElementById('aoi-coords');
        
        if (latlng) {
            areaElement.textContent = 'Point location';
            coordsElement.textContent = `[${latlng.lng.toFixed(6)}, ${latlng.lat.toFixed(6)}] (Marker)`;
            
            // Enable run button
            document.getElementById('run-btn').disabled = false;
        }
    }

    updateAOIInfo() {
        const areaElement = document.getElementById('aoi-area');
        const coordsElement = document.getElementById('aoi-coords');

        if (this.currentMarker) {
            // Handle marker display
            const position = this.currentMarker.getLatLng();
            areaElement.textContent = 'Point location';
            coordsElement.textContent = `[${position.lng.toFixed(6)}, ${position.lat.toFixed(6)}] (Marker)`;
            
            // Enable run button
            document.getElementById('run-btn').disabled = false;
        } else if (this.currentPolygon) {
            // Calculate and display area
            const area = this.calculateArea(this.currentPolygon);
            areaElement.textContent = this.formatArea(area);
            
            // Get coordinates based on shape type
            let coordinates;
            if (this.currentShapeType === 'rectangle') {
                // For rectangles, get the bounds and create corner coordinates
                const bounds = this.currentPolygon.getBounds();
                coordinates = [
                    [bounds.getWest(), bounds.getNorth()],
                    [bounds.getEast(), bounds.getNorth()],
                    [bounds.getEast(), bounds.getSouth()],
                    [bounds.getWest(), bounds.getSouth()],
                    [bounds.getWest(), bounds.getNorth()] // Close the rectangle
                ].map(coord => ({ lng: coord[0], lat: coord[1] }));
            } else {
                // For polygons, get the actual drawn coordinates
                coordinates = this.currentPolygon.getLatLngs()[0];
            }
            
            const coordsList = coordinates.map(coord => 
                `[${coord.lng.toFixed(6)}, ${coord.lat.toFixed(6)}]`
            ).join(', ');
            
            // Show first few and last few coordinates if list is long
            if (coordinates.length > 4) {
                const firstTwo = coordinates.slice(0, 2).map(coord => 
                    `[${coord.lng.toFixed(6)}, ${coord.lat.toFixed(6)}]`
                ).join(', ');
                const lastTwo = coordinates.slice(-2).map(coord => 
                    `[${coord.lng.toFixed(6)}, ${coord.lat.toFixed(6)}]`
                ).join(', ');
                const shapeType = this.currentShapeType === 'rectangle' ? 'Rectangle' : 'Polygon';
                coordsElement.textContent = `${firstTwo} ... ${lastTwo} (${shapeType}, ${coordinates.length} points)`;
            } else {
                const shapeType = this.currentShapeType === 'rectangle' ? 'Rectangle' : 'Polygon';
                coordsElement.textContent = `${coordsList} (${shapeType})`;
            }
            
            // Enable run button
            document.getElementById('run-btn').disabled = false;
        } else {
            areaElement.textContent = 'No area defined';
            coordsElement.textContent = 'None';
            
            // Disable run button
            document.getElementById('run-btn').disabled = true;
        }
    }

    calculateArea(polygon) {
        const latLngs = polygon.getLatLngs()[0];
        let area = 0;
        
        for (let i = 0; i < latLngs.length; i++) {
            const j = (i + 1) % latLngs.length;
            area += latLngs[i].lng * latLngs[j].lat;
            area -= latLngs[j].lng * latLngs[i].lat;
        }
        
        return Math.abs(area) / 2 * 111320 * 111320;
    }

    enableExtractButton() {
        document.getElementById('extract-btn').disabled = false;
    }

    disableExtractButton() {
        document.getElementById('extract-btn').disabled = true;
    }

    async extractFeatures() {
        if (!this.currentPolygon) {
            this.showNotification('Please draw a polygon first', 'error');
            return;
        }

        const requestData = this.buildExtractRequest();

        // Debug logging to help trace the issue
        console.log('Extract request data:', requestData);
        console.log('Current settings:', this.settings);

        // Toast: non-blocking loading for extraction
        if (window.Toast) {
            window.Toast.loading({ id: 'extract', title: 'Extracting features', message: 'Contacting data sources…' });
        }
        // Overlay removed
        
        try {
            // Use the correct V2 API endpoint - FIXED
            const response = await fetch(`/api/v2/extract`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            this.currentJobId = result.job_id;
            
            if (result.status === 'completed') {
                this.displayResults(result);
                this.hideLoadingOverlay();
                if (window.Toast) {
                    window.Toast.success({ id: 'extract', title: 'Extraction complete', message: 'Results are ready' });
                }
                this.showNotification('Features extracted successfully!', 'success');
                document.getElementById('export-btn').disabled = false;
            } else {
                this.pollJobStatus(result.job_id);
            }
        } catch (error) {
            this.hideLoadingOverlay();
            if (window.Toast) {
                window.Toast.error({ id: 'extract', title: 'Extraction failed', message: error.message || 'Please try again' });
            }
            this.showNotification('Extraction failed', 'error');
        }
    }

    buildExtractRequest() {
        const coordinates = this.currentPolygon.getLatLngs()[0].map(latLng => [latLng.lng, latLng.lat]);
        coordinates.push(coordinates[0]);

        // Use settings or defaults for data sources
        const settings = this.settings || {
            dataSourceToggles: {
                googleBuildings: true,
                microsoftBuildings: false,
                osmBuildings: false,
                osmRoads: true,
                osmRailways: false,
                osmLandmarks: true,
                osmNatural: false
            }
        };
        
        const sources = {};
        
        // Configure data sources based on toggle settings (V2 API format)
        if (settings.dataSourceToggles?.googleBuildings) {
            sources.google_buildings = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.microsoftBuildings) {
            sources.microsoft_buildings = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmBuildings) {
            sources.osm_buildings = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmRoads) {
            sources.osm_roads = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmRailways) {
            sources.osm_railways = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmLandmarks) {
            sources.osm_landmarks = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmNatural) {
            sources.osm_natural = { enabled: true, timeout: 30 };
        }

        // Build cleaning configuration if clean data is enabled
        const cleaningConfig = settings.cleanData ? {
            min_area_m2: settings.minBuildingArea || 10,
            overlap_threshold: 0.30,
            edge_buffer_m: 0.5,
            strategy: "highest_confidence",
            simplify_tolerance_m: settings.simplificationTolerance || 0.001,
            make_valid: true
        } : null;

        return {
            aoi_boundary: { type: "Polygon", coordinates: [coordinates] },
            sources: sources,
            clean: !!settings.cleanData,
            cleaning_config: cleaningConfig,
            filters: {
                min_building_area: parseFloat(document.getElementById('min-building-area').value) || null,
                simplification_tolerance: parseFloat(document.getElementById('simplification').value) || 0.001
            }
        };
    }

    async pollJobStatus(jobId) {
        const poll = async () => {
            try {
                // Use the correct V2 API endpoint for job status - FIXED
                const response = await fetch(`/api/v2/job/${jobId}/status?include_results=true`);
                const statusData = await response.json();

                if (statusData.status === 'completed') {
                    // The full results are now included in the status response
                    this.displayResults(statusData.results);
                    this.hideLoadingOverlay();
                    if (window.Toast) {
                        window.Toast.success({ id: 'extract', title: 'Extraction complete', message: 'Results are ready' });
                    }
                    this.showNotification('Extraction completed!', 'success');
                    document.getElementById('export-btn').disabled = false;
                } else if (statusData.status === 'failed') {
                    this.hideLoadingOverlay();
                    if (window.Toast) {
                        window.Toast.error({ id: 'extract', title: 'Extraction failed', message: statusData.message || 'Please try again' });
                    }
                    this.showNotification('Extraction failed', 'error');
                } else {
                    // still running; keep polling
                    setTimeout(poll, 1500);
                }
            } catch (error) {
                this.hideLoadingOverlay();
                if (window.Toast) {
                    window.Toast.error({ id: 'extract', title: 'Extraction failed', message: error.message || 'Please try again' });
                }
                this.showNotification('Extraction failed', 'error');
            }
        };

        poll();
    }

    displayResults(result) {
        // Make results card visible
        const resultsCard = document.getElementById('results-card');
        resultsCard.classList.add('active');
        
        // Hide empty state and show results content
        document.getElementById('results-empty').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';
        
        // Clear existing map layers
        this.dataLayers.forEach(layer => this.map.removeLayer(layer));
        this.dataLayers.clear();
        
        // Update API status
        const statusElement = document.getElementById('api-status');
        statusElement.textContent = 'OK';
        statusElement.className = 'status-value success';
        
        // Display API response
        const responseData = document.getElementById('response-data');
        responseData.textContent = JSON.stringify(result, null, 2);
        
        // Create layer toggles
        const layerToggles = document.getElementById('layer-toggles');
        layerToggles.innerHTML = '';
        
        // Support both full response objects and direct results maps
        const resultsMap = result && result.results ? result.results : result;
        if (!resultsMap || typeof resultsMap !== 'object') {
            this.showNotification('No results to display', 'warning');
            return;
        }

        Object.entries(resultsMap).forEach(([sourceKey, sourceResult]) => {
            const featureCollection = sourceResult?.data || sourceResult?.geojson;
            const features = featureCollection?.features || [];
            const completed = (sourceResult?.status || '').toLowerCase() === 'completed';
            if (completed && features.length > 0) {
                // Create map layer
                const layer = L.geoJSON(featureCollection, {
                    style: this.getLayerStyle(sourceKey)
                });
                
                this.dataLayers.set(sourceKey, layer);
                layer.addTo(this.map);
                
                // Create layer toggle
                const toggle = this.createLayerToggle(sourceKey, sourceResult, true);
                layerToggles.appendChild(toggle);
            }
        });
        
        // Enable download button
        document.getElementById('download-btn').disabled = false;
    }
    
    createLayerToggle(sourceKey, sourceResult, visible = true) {
        const toggle = document.createElement('div');
        toggle.className = 'layer-toggle';
        toggle.dataset.layer = sourceKey;
        
        const sourceName = sourceKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const dataSource = this.getDataSourceName(sourceKey);
        
        toggle.innerHTML = `
            <div class="layer-toggle-info">
                <div class="layer-name">${sourceName}</div>
                <div class="layer-source">Source: ${dataSource} (${(sourceResult?.stats && sourceResult.stats.count) || (sourceResult?.data?.features?.length || sourceResult?.geojson?.features?.length || 0)} features)</div>
            </div>
            <div class="layer-switch ${visible ? 'active' : ''}" data-layer="${sourceKey}"></div>
        `;
        
        // Add click event
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleLayer(sourceKey);
        });
        
        return toggle;
    }
    
    getDataSourceName(sourceKey) {
        const sourceMap = {
            'microsoft_buildings': 'Microsoft Building Footprints',
            'google_buildings': 'Google Open Buildings',
            'osm_buildings': 'OpenStreetMap',
            'osm_roads': 'OpenStreetMap',
            'osm_railways': 'OpenStreetMap',
            'osm_landmarks': 'OpenStreetMap',
            'osm_natural': 'OpenStreetMap'
        };
        return sourceMap[sourceKey] || 'Unknown';
    }
    
    toggleLayer(sourceKey) {
        const layer = this.dataLayers.get(sourceKey);
        const switchElement = document.querySelector(`[data-layer="${sourceKey}"].layer-switch`);
        
        if (layer && switchElement) {
            if (this.map.hasLayer(layer)) {
                this.map.removeLayer(layer);
                switchElement.classList.remove('active');
            } else {
                this.map.addLayer(layer);
                switchElement.classList.add('active');
            }
        }
    }

    cancelExtraction() {
        // Cancel any ongoing extraction
        this.hideLoadingOverlay();
        this.showNotification('Extraction cancelled', 'info');
    }

    toggleResults() {
        const toggle = document.getElementById('results-toggle');
        const resultsCard = document.getElementById('results-card');
        
        if (toggle && resultsCard) {
            toggle.classList.toggle('active');
            if (toggle.classList.contains('active')) {
                resultsCard.style.display = 'block';
                // Show all data layers
                this.dataLayers.forEach(layer => {
                    if (!this.map.hasLayer(layer)) {
                        this.map.addLayer(layer);
                    }
                });
            } else {
                // Hide all data layers but keep the results card visible
                this.dataLayers.forEach(layer => {
                    if (this.map.hasLayer(layer)) {
                        this.map.removeLayer(layer);
                    }
                });
            }
        }
    }

    openSettingsModal() {
        document.getElementById('settings-modal').classList.remove('hidden');
    }
    
    closeSettingsModal() {
        document.getElementById('settings-modal').classList.add('hidden');
    }
    
    applySettings() {
        // Get settings values
        const outputFormat = document.querySelector('input[name="output-format"]:checked')?.value || 'kmz';

        // Get data source toggle states
        const dataSourceToggles = {
            googleBuildings: document.getElementById('toggle-google-buildings').checked,
            microsoftBuildings: document.getElementById('toggle-microsoft-buildings').checked,
            osmBuildings: document.getElementById('toggle-osm-buildings').checked,
            osmRoads: document.getElementById('toggle-osm-roads').checked,
            osmRailways: document.getElementById('toggle-osm-railways').checked,
            osmLandmarks: document.getElementById('toggle-osm-landmarks').checked,
            osmNatural: document.getElementById('toggle-osm-natural').checked
        };

        // Store settings for later use
        this.settings = {
            outputFormat,
            dataSourceToggles,
            cleanData: document.getElementById('clean-data-setting')?.checked || false,
            cleanRoads: document.getElementById('clean-roads-setting')?.checked || false,
            minBuildingArea: parseFloat(document.getElementById('min-building-area-setting').value) || 10,
            simplificationTolerance: parseFloat(document.getElementById('simplification-setting').value) || 0.001,
            // Advanced building params
            googleConfidence: parseFloat(document.getElementById('google-confidence-setting')?.value) || 0.7,
            minWidth: parseFloat(document.getElementById('min-width-setting')?.value) || 3,
            minCompactness: parseFloat(document.getElementById('min-compactness-setting')?.value) || 0.12,
            maxElongation: parseFloat(document.getElementById('max-elongation-setting')?.value) || 6,
            roadTypes: Array.from(document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked')).map(cb => cb.value)
        };

        // ALSO handle map source preferences (merged from the duplicate method)
        const streetSelect = document.getElementById('street-source-setting');
        const satelliteSelect = document.getElementById('satellite-source-setting');
        const terrainSelect = document.getElementById('terrain-source-setting');

        // Update user preferences
        if (streetSelect) {
            this.userMapPreferences.streets = streetSelect.value;
        }
        if (satelliteSelect) {
            this.userMapPreferences.satellite = satelliteSelect.value;
        }
        if (terrainSelect) {
            this.userMapPreferences.terrain = terrainSelect.value;
        }

        // Save map preferences
        this.saveMapPreferences();

        // Update current map if needed
        const currentMapType = document.getElementById('map-type-selector').value;
        this.changeMapType(currentMapType);

        // Update layer cycling display
        this.updateLayerCyclingDisplay();

        this.closeSettingsModal();
        this.showNotification('Settings saved successfully!', 'success');

        // Debug logging to help trace the issue
        console.log('Settings applied:', this.settings);
    }
    
    async runAnalysis() {
        if (!this.currentPolygon && !this.currentMarker) {
            this.showNotification('Please draw an area or place a marker first', 'error');
            return;
        }
        
        const requestData = this.buildAnalysisRequest();
        // Overlay removed: rely on toasts only
        if (window.Toast) {
            window.Toast.loading({ id: 'analysis', title: 'Running analysis', message: 'Aggregating sources…' });
        }
        
        try {
            // Use the correct V2 API endpoint - FIXED
            const response = await fetch(`/api/v2/extract`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.currentJobId = result.job_id;
            
            if (result.status === 'completed') {
                this.displayResults(result);
                this.hideLoadingOverlay();
                if (window.Toast) {
                    window.Toast.success({ id: 'analysis', title: 'Analysis complete', message: 'Results are ready' });
                }
                this.showNotification('Analysis completed successfully!', 'success');
            } else {
                this.pollJobStatus(result.job_id);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.hideLoadingOverlay();
            if (window.Toast) {
                window.Toast.error({ id: 'analysis', title: 'Analysis failed', message: error.message || 'Please try again' });
            }
            this.showNotification(`Analysis failed: ${error.message}`, 'error');
        }
    }
    
    buildAnalysisRequest() {
        let coordinates;
        
        if (this.currentMarker) {
            // For markers, create a small buffer area around the point
            const position = this.currentMarker.getLatLng();
            const buffer = 0.001; // ~100m buffer
            coordinates = [
                [position.lng - buffer, position.lat + buffer],
                [position.lng + buffer, position.lat + buffer],
                [position.lng + buffer, position.lat - buffer],
                [position.lng - buffer, position.lat - buffer],
                [position.lng - buffer, position.lat + buffer] // Close the polygon
            ];
        } else if (this.currentShapeType === 'rectangle') {
            // For rectangles, get bounds and create corner coordinates
            const bounds = this.currentPolygon.getBounds();
            coordinates = [
                [bounds.getWest(), bounds.getNorth()],
                [bounds.getEast(), bounds.getNorth()],
                [bounds.getEast(), bounds.getSouth()],
                [bounds.getWest(), bounds.getSouth()],
                [bounds.getWest(), bounds.getNorth()] // Close the rectangle
            ];
        } else {
            // For polygons, get the actual drawn coordinates
            coordinates = this.currentPolygon.getLatLngs()[0].map(latLng => [latLng.lng, latLng.lat]);
            coordinates.push(coordinates[0]); // Close the polygon
        }
        
        // Use applied settings; if not applied yet, snapshot current UI state
        const settings = this.settings || this.getSettingsSnapshotFromUI();
        
        const sources = {};
        
        // Configure data sources based on toggle settings (V2 API format)
        if (settings.dataSourceToggles?.googleBuildings) {
            sources.google_buildings = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.microsoftBuildings) {
            sources.microsoft_buildings = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmBuildings) {
            sources.osm_buildings = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmRoads) {
            sources.osm_roads = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmRailways) {
            sources.osm_railways = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmLandmarks) {
            sources.osm_landmarks = { enabled: true, timeout: 30 };
        }
        if (settings.dataSourceToggles?.osmNatural) {
            sources.osm_natural = { enabled: true, timeout: 30 };
        }
        
        const payload = {
            aoi_boundary: { type: "Polygon", coordinates: [coordinates] },
            sources: sources,  // Changed from 'data_sources' to 'sources' - FIXED
            clean: !!settings.cleanData,
            clean_roads: !!settings.cleanRoads
        };

        // Include cleaning_config only when buildings cleaning is enabled
        if (payload.clean) {
            payload.cleaning_config = {
                min_area_m2: Number.isFinite(settings.minBuildingArea) ? settings.minBuildingArea : 12,
                simplify_tolerance_m: Number.isFinite(settings.simplificationTolerance) ? settings.simplificationTolerance : 0.001,
                google_min_confidence: Number.isFinite(settings.googleConfidence) ? settings.googleConfidence : 0.7,
                min_width_m: Number.isFinite(settings.minWidth) ? settings.minWidth : 3,
                min_compactness: Number.isFinite(settings.minCompactness) ? settings.minCompactness : 0.12,
                max_elongation: Number.isFinite(settings.maxElongation) ? settings.maxElongation : 6,
                strategy: 'highest_confidence',
                make_valid: true,
            };
        }

        return payload;
    }

    // Snapshot current UI state without requiring Apply, used by buildAnalysisRequest()
    getSettingsSnapshotFromUI() {
        const outputFormat = (document.querySelector('input[name="output-format"]:checked')?.value) || 'kmz';
        const dataSourceToggles = {
            googleBuildings: document.getElementById('toggle-google-buildings')?.checked || false,
            microsoftBuildings: document.getElementById('toggle-microsoft-buildings')?.checked || false,
            osmBuildings: document.getElementById('toggle-osm-buildings')?.checked || false,
            osmRoads: document.getElementById('toggle-osm-roads')?.checked || false,
            osmRailways: document.getElementById('toggle-osm-railways')?.checked || false,
            osmLandmarks: document.getElementById('toggle-osm-landmarks')?.checked || false,
            osmNatural: document.getElementById('toggle-osm-natural')?.checked || false,
        };
        const cleanData = document.getElementById('clean-data-setting')?.checked || false;
        const cleanRoads = document.getElementById('clean-roads-setting')?.checked || false;
        const minBuildingArea = parseFloat(document.getElementById('min-building-area-setting')?.value) || 10;
        const simplificationTolerance = parseFloat(document.getElementById('simplification-setting')?.value) || 0.001;
        const googleConfidence = parseFloat(document.getElementById('google-confidence-setting')?.value) || 0.7;
        const minWidth = parseFloat(document.getElementById('min-width-setting')?.value) || 3;
        const minCompactness = parseFloat(document.getElementById('min-compactness-setting')?.value) || 0.12;
        const maxElongation = parseFloat(document.getElementById('max-elongation-setting')?.value) || 6;
        const roadTypes = Array.from(document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked')).map(cb => cb.value);

        return {
            outputFormat,
            dataSourceToggles,
            cleanData,
            cleanRoads,
            minBuildingArea,
            simplificationTolerance,
            googleConfidence,
            minWidth,
            minCompactness,
            maxElongation,
            roadTypes,
        };
    }
    
    toggleResponse() {
        const toggle = document.getElementById('response-toggle');
        const content = document.getElementById('response-content');
        
        if (toggle && content) {
            toggle.classList.toggle('expanded');
            content.classList.toggle('visible');
        }
    }
    
    async downloadResults() {
        if (!this.currentJobId) {
            this.showNotification('No results to download', 'error');
            return;
        }

        const format = this.settings?.outputFormat || 'kmz';

        try {
            // Try normal job-based download first
            const response = await fetch(`/api/v2/download/${this.currentJobId}/${format}`);

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `atlas_results_${this.currentJobId}.${format}`;
                a.click();
                window.URL.revokeObjectURL(url);

                // Hide loading overlay and show success notification
                this.hideLoadingOverlay();
                this.showNotification('Download completed successfully!', 'success');
                return;
            }
            
            // If 404, fall back to inline export using the current results payload
            if (response.status === 404) {
                const responseData = document.getElementById('response-data').textContent;
                let parsed;
                try { parsed = JSON.parse(responseData); } catch (_) { parsed = null; }
                const resultsMap = parsed && parsed.results ? parsed.results : parsed;
                if (!resultsMap) throw new Error('No results available for inline export');
                
                const inlineRes = await fetch(`/api/v2/download-inline/${format}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ results: resultsMap })
                });
                if (!inlineRes.ok) {
                    throw new Error(`HTTP ${inlineRes.status}: ${inlineRes.statusText}`);
                }
                const blob = await inlineRes.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `atlas_results_${this.currentJobId || 'inline'}.${format}`;
                a.click();
                window.URL.revokeObjectURL(url);

                // Hide loading overlay and show success notification
                this.hideLoadingOverlay();
                this.showNotification('Download completed successfully!', 'success');
                return;
            }
            
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        } catch (error) {
            console.error('Download error:', error);
            // Hide loading overlay on error
            this.hideLoadingOverlay();
            this.showNotification(`Download failed: ${error.message}`, 'error');
        }
    }

    getLayerStyle(sourceKey) {
        const styles = {
            microsoft_buildings: { color: '#dc2626', weight: 1, fillOpacity: 0.3 },
            google_buildings: { color: '#ea580c', weight: 1, fillOpacity: 0.3 },
            osm_buildings: { color: '#ca8a04', weight: 1, fillOpacity: 0.3 },
            osm_roads: { color: '#2563eb', weight: 2, fillOpacity: 0 },
            osm_railways: { color: '#059669', weight: 3, fillOpacity: 0 },
            osm_landmarks: { color: '#7c3aed', weight: 1, fillOpacity: 0.5 }
        };
        return styles[sourceKey] || { color: '#64748b', weight: 1, fillOpacity: 0.3 };
    }

    createResultItem(sourceKey, sourceResult) {
        const item = document.createElement('div');
        item.className = 'result-item';
        const sourceName = sourceKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        item.innerHTML = `
            <div class="result-header">
                <span class="result-name">${sourceName}</span>
                <span class="result-status ${sourceResult.status}">${sourceResult.status}</span>
            </div>
            <div class="result-stats">${sourceResult.stats.count} features</div>
        `;
        return item;
    }

    updateLayerPanel() {
        const layerList = document.querySelector('.layer-list');
        layerList.innerHTML = '';

        this.dataLayers.forEach((layer, sourceKey) => {
            const sourceName = sourceKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            const layerItem = document.createElement('label');
            layerItem.className = 'checkbox-label';
            layerItem.innerHTML = `
                <input type="checkbox" data-layer="${sourceKey}" checked>
                <span class="checkmark"></span>
                <span>${sourceName}</span>
            `;

            layerItem.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.map.addLayer(layer);
                } else {
                    this.map.removeLayer(layer);
                }
            });

            layerList.appendChild(layerItem);
        });
    }

    toggleLayerPanel() {
        const layerPanel = document.getElementById('layer-panel');
        if (layerPanel) {
            layerPanel.classList.toggle('hidden');
        } else {
            // Show layer information in results toggle instead
            this.showNotification('Layer visibility can be controlled via the results toggle', 'info');
        }
    }

    showExportModal() {
        if (!this.currentJobId) {
            this.showNotification('No data to export', 'error');
            return;
        }

        const sourceCheckboxes = document.querySelector('.source-checkboxes');
        sourceCheckboxes.innerHTML = '';

        this.dataLayers.forEach((layer, sourceKey) => {
            const sourceName = sourceKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const checkboxItem = document.createElement('label');
            checkboxItem.className = 'checkbox-label';
            checkboxItem.innerHTML = `
                <input type="checkbox" value="${sourceKey}" checked>
                <span class="checkmark"></span>
                <span>${sourceName}</span>
            `;
            sourceCheckboxes.appendChild(checkboxItem);
        });

        document.getElementById('export-modal').classList.remove('hidden');
    }

    hideExportModal() {
        document.getElementById('export-modal').classList.add('hidden');
    }

    async performExport() {
        const format = document.querySelector('input[name="export-format"]:checked').value;
        const selectedSources = Array.from(document.querySelectorAll('.source-checkboxes input:checked')).map(cb => cb.value);

        // Show loading overlay during export
        if (window.Toast) {
            window.Toast.loading({ id: 'export', title: 'Preparing export', message: `Format: ${format.toUpperCase()}` });
        }
        this.showLoadingOverlay('Preparing your export, thank you...');

        try {
            // Use the correct V2 API endpoint for export - FIXED
            const response = await fetch(`/api/v2/download/${this.currentJobId}/${format}`);
            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `atlas_export_${this.currentJobId}.${format}`;
            a.click();
            window.URL.revokeObjectURL(url);

            // Hide loading overlay and export modal
            this.hideLoadingOverlay();
            this.hideExportModal();
            if (window.Toast) {
                window.Toast.success({ id: 'export', title: 'Export ready', message: 'Saving file…' });
            }
            this.showNotification('Export completed successfully!', 'success');
        } catch (error) {
            // Hide loading overlay on error
            this.hideLoadingOverlay();
            if (window.Toast) {
                window.Toast.error({ id: 'export', title: 'Export failed', message: error.message || 'Please try again' });
            }
            this.showNotification('Export failed', 'error');
        }
    }

    showLoadingOverlay(message) {
        // Gracefully no-op if the overlay elements are not present.
        const msgEl = document.getElementById('loading-message');
        const overlay = document.getElementById('loading-overlay');
        if (msgEl) msgEl.textContent = message || '';
        if (overlay) overlay.classList.remove('hidden');
        // If overlay is missing, rely on Toasts (already integrated elsewhere)
        if (!overlay && window.Toast) {
            // Do not show an extra toast here to avoid duplicates; leave as no-op
            // window.Toast.info({ title: 'Working…', message });
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('hidden');
        // Otherwise, nothing to do
    }

    showNotification(message, type = 'info') {
        // Prefer unified Toast service for all notifications
        if (window.Toast) {
            const titleMap = { success: 'Success', error: 'Error', warning: 'Warning', info: 'Notice', loading: 'Working…' };
            const method = window.Toast[type] || window.Toast.info;
            method({ title: titleMap[type] || 'Notice', message });
            return;
        }
        // Fallback (Toast not loaded): minimal non-blocking banner
        const notification = document.createElement('div');
        notification.className = `atlasomi-notification atlasomi-notification-${type}`;
        notification.style.cssText = `
            position: fixed; bottom: 20px; right: 20px; z-index: 4000;
            background: ${type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : type === 'warning' ? '#d97706' : '#0e5a81'};
            color: white; padding: 0.875rem 1.25rem; border-radius: 0.5rem; border-left: 3px solid rgba(255,255,255,0.6);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2); cursor: pointer;
            transform: translateY(100%); transition: transform 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => { notification.style.transform = 'translateY(0)'; }, 10);
        setTimeout(() => {
            notification.style.transform = 'translateY(100%)';
            setTimeout(() => { if (notification.parentNode) notification.parentNode.removeChild(notification); }, 300);
        }, 4000);
        notification.addEventListener('click', () => { if (notification.parentNode) notification.parentNode.removeChild(notification); });
    }

    /**
     * Utility function to validate coordinates
     */
    validateCoordinates(lat, lng) {
        return !isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    }

    /**
     * Utility function to format area display
     */
    formatArea(areaM2) {
        if (areaM2 < 1000000) {
            return `${(areaM2 / 10000).toFixed(2)} hectares`;
        } else {
            return `${(areaM2 / 1000000).toFixed(2)} km²`;
        }
    }

    /**
     * Utility function to debounce function calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initialize map sources configuration
    initializeMapSources() {
        return {
            streets: {
                osm: {
                    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    subdomains: ['a', 'b', 'c'],
                    maxZoom: 19
                },
                google: {
                    url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                    attribution: '&copy; Google',
                    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
                    maxZoom: 20
                },
                carto_light: {
                    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    subdomains: ['a', 'b', 'c', 'd'],
                    maxZoom: 19
                },
                carto_dark: {
                    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    subdomains: ['a', 'b', 'c', 'd'],
                    maxZoom: 19
                },
                wikimedia: {
                    url: 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}{r}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://wikimediafoundation.org/wiki/Maps_Terms_of_Use">Wikimedia maps</a>',
                    subdomains: ['a', 'b', 'c'],
                    maxZoom: 19
                }
            },
            satellite: {
                esri: {
                    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community',
                    maxZoom: 19
                },
                google: {
                    url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                    attribution: '&copy; Google',
                    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
                    maxZoom: 20
                },
                google_hybrid: {
                    url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                    attribution: '&copy; Google',
                    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
                    maxZoom: 20
                }
            },
            terrain: {
                opentopo: {
                    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
                    subdomains: ['a', 'b', 'c'],
                    maxZoom: 17
                },
                google: {
                    url: 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}',
                    attribution: '&copy; Google',
                    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
                    maxZoom: 20
                },
                stamen: {
                    url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
                    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                    subdomains: ['a', 'b', 'c', 'd'],
                    maxZoom: 18
                },
                usgs: {
                    url: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
                    attribution: 'USGS',
                    maxZoom: 16
                }
            }
        };
    }

    // Get default source for each map type
    getDefaultSource(mapType) {
        const defaults = {
            streets: 'google',
            satellite: 'google_hybrid',
            terrain: 'usgs'
        };
        return defaults[mapType] || 'osm';
    }

    // Load user map preferences from localStorage
    loadMapPreferences() {
        try {
            const saved = localStorage.getItem('atlas_map_preferences');
            return saved ? JSON.parse(saved) : {};
        } catch (error) {
            console.warn('Error loading map preferences:', error);
            return {};
        }
    }

    // Save user map preferences to localStorage
    saveMapPreferences() {
        try {
            localStorage.setItem('atlas_map_preferences', JSON.stringify(this.userMapPreferences));
        } catch (error) {
            console.warn('Error saving map preferences:', error);
        }
    }

    // Open settings modal and populate map source selections
    openSettingsModal() {
        const modal = document.getElementById('settings-modal');
        modal.classList.remove('hidden');
        
        // Populate current map source selections
        this.populateMapSourceSettings();
    }

    // Close settings modal
    closeSettingsModal() {
        const modal = document.getElementById('settings-modal');
        modal.classList.add('hidden');
    }

    // Populate map source dropdowns with current selections
    populateMapSourceSettings() {
        const streetSelect = document.getElementById('street-source-setting');
        const satelliteSelect = document.getElementById('satellite-source-setting');
        const terrainSelect = document.getElementById('terrain-source-setting');

        if (streetSelect) {
            streetSelect.value = this.userMapPreferences.streets || this.getDefaultSource('streets');
        }
        if (satelliteSelect) {
            satelliteSelect.value = this.userMapPreferences.satellite || this.getDefaultSource('satellite');
        }
        if (terrainSelect) {
            terrainSelect.value = this.userMapPreferences.terrain || this.getDefaultSource('terrain');
        }
    }



    // Setup layer cycling control
    setupLayerCycling() {
        const cycleBtn = document.getElementById('layer-cycle-btn');
        if (cycleBtn) {
            cycleBtn.addEventListener('click', () => this.cycleMapSource());
        }
        
        // Initialize display
        this.updateLayerCyclingDisplay();
    }

    // Get available sources for current map type
    getAvailableSourcesForMapType(mapType) {
        const sourceOrder = {
            streets: ['google', 'osm', 'carto_light', 'carto_dark', 'wikimedia'],
            satellite: ['google_hybrid', 'google', 'esri'],
            terrain: ['usgs', 'opentopo', 'google', 'stamen']
        };
        return sourceOrder[mapType] || ['osm'];
    }

    // Get display name for source
    getSourceDisplayName(mapType, sourceKey) {
        const displayNames = {
            streets: {
                osm: 'OpenStreetMap',
                google: 'Google Streets',
                carto_light: 'CartoDB Light',
                carto_dark: 'CartoDB Dark',
                wikimedia: 'Wikimedia'
            },
            satellite: {
                esri: 'Esri Satellite',
                google: 'Google Satellite',
                google_hybrid: 'Google Hybrid'
            },
            terrain: {
                opentopo: 'OpenTopoMap',
                google: 'Google Terrain',
                stamen: 'Stamen Terrain',
                usgs: 'USGS Topo'
            }
        };
        return displayNames[mapType]?.[sourceKey] || sourceKey;
    }

    // Cycle to next map source for current map type
    cycleMapSource() {
        const currentMapType = document.getElementById('map-type-selector').value;
        const availableSources = this.getAvailableSourcesForMapType(currentMapType);
        const currentSource = this.userMapPreferences[currentMapType] || this.getDefaultSource(currentMapType);
        
        // Find current index and get next source
        const currentIndex = availableSources.indexOf(currentSource);
        const nextIndex = (currentIndex + 1) % availableSources.length;
        const nextSource = availableSources[nextIndex];
        
        // Update preference
        this.userMapPreferences[currentMapType] = nextSource;
        this.saveMapPreferences();
        
        // Update map
        this.changeMapType(currentMapType);
        
        // Update display
        this.updateLayerCyclingDisplay();
        
        // Show notification
        const sourceName = this.getSourceDisplayName(currentMapType, nextSource);
        this.showNotification(`Switched to ${sourceName}`, 'info');
    }

    // Update layer cycling display
    updateLayerCyclingDisplay() {
        const currentMapType = document.getElementById('map-type-selector').value;
        const currentSource = this.userMapPreferences[currentMapType] || this.getDefaultSource(currentMapType);
        const sourceName = this.getSourceDisplayName(currentMapType, currentSource);
        
        const sourceNameElement = document.getElementById('current-source-name');
        if (sourceNameElement) {
            sourceNameElement.textContent = sourceName;
        }
    }
}

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AtlasomiInterface();
});