import React, { useState, useEffect } from 'react';
import { 
  MapIcon,
  DocumentArrowUpIcon,
  PlayIcon,
  StopIcon,
  CogIcon,
  EyeIcon,
  EyeSlashIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';
import type { AOIDrawingState, JobStatus } from '@/shared/types';
import { useAppSession } from '@/react-app/hooks/useStorage';
import { useStorage } from '@/react-app/context/StorageContext';

// Mock map component - will be replaced with actual Leaflet map
const MapContainer: React.FC = () => {
  return (
    <div className="w-full h-full bg-lasomi-sidebar border border-border rounded-md flex items-center justify-center">
      <div className="text-center">
        <MapIcon className="w-12 h-12 text-text-secondary mx-auto mb-4" />
        <h3 className="text-lg font-medium text-text-primary mb-2">Interactive Map</h3>
        <p className="text-text-secondary">Leaflet map will be integrated here</p>
      </div>
    </div>
  );
};

interface DesignerState {
  aoiState: AOIDrawingState;
  jobStatus: JobStatus | null;
  dataSources: Record<string, boolean>;
}

const defaultState: DesignerState = {
  aoiState: {
    isDrawing: false,
    drawingMode: null,
  },
  jobStatus: null,
  dataSources: {
    'Microsoft Buildings': true,
    'Google Buildings': true,
    'OSM Buildings': false,
    'OSM Roads': true,
    'OSM Railways': false,
  }
};

const AOIPanel: React.FC = () => {
  const { logActivity } = useStorage();
  const { 
    state: designerState, 
    setState: setDesignerState, 
    loading: sessionLoading 
  } = useAppSession<DesignerState>('designer', defaultState);

  const [aoiState, setAoiState] = useState<AOIDrawingState>(designerState.aoiState);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(designerState.jobStatus);
  const [dataSources, setDataSources] = useState(designerState.dataSources);

  // Save state to session when it changes
  useEffect(() => {
    if (!sessionLoading) {
      setDesignerState({
        aoiState,
        jobStatus,
        dataSources
      });
    }
  }, [aoiState, jobStatus, dataSources, setDesignerState, sessionLoading]);

  const handleStartDrawing = async (mode: 'polygon' | 'rectangle') => {
    const newState = {
      isDrawing: true,
      drawingMode: mode,
    };
    setAoiState(newState);

    await logActivity({
      action: 'start_drawing',
      appId: 'designer',
      appName: 'Designer',
      description: `Started drawing ${mode} AOI`,
      data: { mode }
    });
  };

  const handleClearAOI = async () => {
    const newState = {
      isDrawing: false,
      drawingMode: null,
      currentAOI: undefined,
    };
    setAoiState(newState);

    await logActivity({
      action: 'clear_aoi',
      appId: 'designer',
      appName: 'Designer',
      description: 'Cleared AOI drawing'
    });
  };

  const handleRunExtraction = async () => {
    // Mock job creation
    const newJobStatus = {
      id: 'job-123',
      status: 'processing' as const,
      progress: 0,
      message: 'Starting building extraction...'
    };
    setJobStatus(newJobStatus);

    await logActivity({
      action: 'start_extraction',
      appId: 'designer',
      appName: 'Designer',
      description: 'Started feature extraction job',
      data: { 
        jobId: newJobStatus.id,
        aoi: aoiState.currentAOI,
        sources: Object.entries(dataSources).filter(([_, enabled]) => enabled).map(([name]) => name)
      }
    });

    // Simulate progress
    setTimeout(() => {
      setJobStatus(prev => prev ? { ...prev, progress: 50, message: 'Extracting from Microsoft Buildings...' } : null);
    }, 2000);

    setTimeout(async () => {
      const completedStatus = { 
        id: 'job-123',
        status: 'completed' as const, 
        progress: 100, 
        message: 'Extraction completed' 
      };
      setJobStatus(completedStatus);

      await logActivity({
        action: 'extraction_completed',
        appId: 'designer',
        appName: 'Designer',
        description: 'Feature extraction completed successfully'
      });
    }, 4000);
  };

  const toggleDataSource = async (sourceName: string) => {
    const newDataSources = {
      ...dataSources,
      [sourceName]: !dataSources[sourceName]
    };
    setDataSources(newDataSources);

    await logActivity({
      action: 'toggle_data_source',
      appId: 'designer',
      appName: 'Designer',
      description: `${newDataSources[sourceName] ? 'Enabled' : 'Disabled'} ${sourceName}`,
      data: { sourceName, enabled: newDataSources[sourceName] }
    });
  };

  return (
    <div className="w-80 bg-lasomi-sidebar border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-text-primary">Designer</h2>
        <p className="text-sm text-text-secondary">Define areas and extract features</p>
      </div>

      {/* Upload Design Section */}
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-medium text-text-primary mb-3">Upload Design</h3>
        <div className="border-2 border-dashed border-border rounded-md p-4 text-center hover:border-lasomi-primary transition-colors cursor-pointer">
          <DocumentArrowUpIcon className="w-8 h-8 text-text-secondary mx-auto mb-2" />
          <p className="text-xs text-text-secondary">
            Drop KMZ/KML files here or click to browse
          </p>
        </div>
      </div>

      {/* AOI Drawing Section */}
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-medium text-text-primary mb-3">Area of Interest</h3>
        
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => handleStartDrawing('polygon')}
            className={`btn ${aoiState.drawingMode === 'polygon' ? 'btn-primary' : 'btn-secondary'} flex-1 text-xs`}
          >
            Draw Polygon
          </button>
          <button
            onClick={() => handleStartDrawing('rectangle')}
            className={`btn ${aoiState.drawingMode === 'rectangle' ? 'btn-primary' : 'btn-secondary'} flex-1 text-xs`}
          >
            Draw Rectangle
          </button>
        </div>

        {aoiState.currentAOI ? (
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-text-secondary">Area:</span>
              <span className="text-text-primary">{aoiState.currentAOI.area.toFixed(2)} km²</span>
            </div>
            <button
              onClick={handleClearAOI}
              className="btn btn-ghost w-full text-xs"
            >
              Clear AOI
            </button>
          </div>
        ) : (
          <p className="text-xs text-text-secondary">Draw an area to get started</p>
        )}
      </div>

      {/* Data Sources Section */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-text-primary">Data Sources</h3>
          <button className="p-1 text-text-secondary hover:text-text-primary">
            <CogIcon className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2">
          {Object.entries(dataSources).map(([name, enabled]) => (
            <div key={name} className="flex items-center justify-between">
              <span className="text-xs text-text-secondary">{name}</span>
              <button 
                className="p-1" 
                onClick={() => toggleDataSource(name)}
                title={`${enabled ? 'Disable' : 'Enable'} ${name}`}
              >
                {enabled ? (
                  <EyeIcon className="w-4 h-4 text-success" />
                ) : (
                  <EyeSlashIcon className="w-4 h-4 text-text-secondary" />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Actions Section */}
      <div className="p-4 flex-1 flex flex-col justify-end">
        {jobStatus && (
          <div className="mb-4 p-3 bg-lasomi-card border border-border rounded-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-text-primary">Processing</span>
              <span className="text-xs text-text-secondary">{jobStatus.progress}%</span>
            </div>
            <div className="w-full bg-lasomi-secondary rounded-full h-1.5 mb-2">
              <div 
                className="bg-lasomi-primary h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${jobStatus.progress}%` }}
              ></div>
            </div>
            <p className="text-xs text-text-secondary">{jobStatus.message}</p>
          </div>
        )}

        <div className="space-y-2">
          <button
            onClick={handleRunExtraction}
            disabled={!aoiState.currentAOI || jobStatus?.status === 'processing'}
            className="btn btn-primary w-full"
          >
            {jobStatus?.status === 'processing' ? (
              <>
                <StopIcon className="w-4 h-4" />
                Processing...
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4" />
                Run Extraction
              </>
            )}
          </button>

          <button
            disabled={jobStatus?.status !== 'completed'}
            className="btn btn-secondary w-full"
          >
            <DocumentArrowDownIcon className="w-4 h-4" />
            Export Results
          </button>
        </div>
      </div>
    </div>
  );
};

export default function Designer() {
  return (
    <div className="flex h-full">
      {/* Control Panel */}
      <AOIPanel />

      {/* Map Area */}
      <div className="flex-1 p-4">
        <MapContainer />
      </div>
    </div>
  );
}
