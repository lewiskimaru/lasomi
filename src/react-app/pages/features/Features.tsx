import React, { useState, useEffect } from 'react';
import { 
  DocumentArrowUpIcon,
  PlayIcon,
  StopIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';
import type { AOIDrawingState, JobStatus } from '@/shared/types';
import { useAppSession } from '@/react-app/hooks/useStorage';
import { useStorage } from '@/react-app/context/StorageContext';
import MapComponent from '@/react-app/components/map/MapComponent';

interface FeaturesState {
  aoiState: AOIDrawingState;
  jobStatus: JobStatus | null;
  dataSources: Record<string, boolean>;
}

const defaultState: FeaturesState = {
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

const AOIPanel: React.FC<{
  aoiState: AOIDrawingState;
  jobStatus: JobStatus | null;
  dataSources: Record<string, boolean>;
  uploadedFile: File | null;
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onRunExtraction: () => void;
  onToggleDataSource: (sourceName: string) => void;
}> = ({
  aoiState,
  jobStatus,
  dataSources,
  uploadedFile,
  onFileUpload,
  onRunExtraction,
  onToggleDataSource
}) => {

  return (
    <div className="w-80 space-y-8 overflow-y-auto">
      {/* Design Upload & Settings Card */}
      <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-md p-4">
        <h3 className="text-sm font-semibold text-text-primary mb-4">Upload Design & Settings</h3>
        
        {/* File Upload Section */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-text-primary mb-2">
            Upload Design File (KML, GeoJSON)
          </label>
          <div className="relative">
            <input
              type="file"
              accept=".kml,.geojson,.json"
              onChange={onFileUpload}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="flex items-center justify-center w-full px-3 py-2 border border-border rounded-md text-sm text-text-primary bg-lasomi-card hover:bg-lasomi-secondary cursor-pointer transition-colors"
            >
              <DocumentArrowUpIcon className="w-4 h-4 mr-2" />
              {uploadedFile ? uploadedFile.name : 'Choose file...'}
            </label>
          </div>
        </div>

        {/* Data Sources Settings */}
        <div>
          <label className="block text-xs font-medium text-text-primary mb-2">
            Data Sources
          </label>
          <div className="space-y-2">
            {Object.entries(dataSources).map(([sourceName, enabled]) => (
              <label key={sourceName} className="flex items-center">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={() => onToggleDataSource(sourceName)}
                  className="h-3 w-3 text-lasomi-primary border-border rounded focus:ring-lasomi-primary bg-lasomi-card"
                />
                <span className="ml-2 text-xs text-text-primary">{sourceName}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Area Drawing Card */}
      <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-md p-4">
        <h3 className="text-sm font-semibold text-text-primary mb-4">Area Information</h3>
        
        {aoiState.currentAOI ? (
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-text-secondary">Status:</span>
              <span className="text-text-primary">Area Selected</span>
            </div>
            <div className="p-2 bg-lasomi-secondary/50 border border-border rounded-md">
              <p className="text-xs text-text-secondary">
                Use the map drawing tools to create or modify areas. Click the polygon or rectangle icons on the map.
              </p>
            </div>
          </div>
        ) : (
          <div className="p-2 bg-lasomi-secondary/30 border border-border/50 rounded-md">
            <p className="text-xs text-text-secondary">
              No area selected. Use the drawing tools on the map (top-left corner) to create an area of interest.
            </p>
          </div>
        )}

        {aoiState.isDrawing && (
          <div className="mt-3 p-2 bg-lasomi-primary/20 border border-lasomi-primary/30 rounded-md">
            <p className="text-xs text-text-primary">
              Drawing {aoiState.drawingMode}... Check the map for instructions.
            </p>
          </div>
        )}
      </div>

      {/* Analysis & Export Card */}
      <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-md p-4">
        <h3 className="text-sm font-semibold text-text-primary mb-4">Run Analysis</h3>
        
        {/* Progress Section */}
        {jobStatus && (
          <div className="mb-4 p-3 bg-lasomi-secondary border border-border rounded-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-text-primary">Processing</span>
              <span className="text-xs text-text-secondary">{jobStatus.progress}%</span>
            </div>
            <div className="w-full bg-lasomi-page rounded-full h-1.5 mb-2">
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
            onClick={onRunExtraction}
            disabled={!aoiState.currentAOI || jobStatus?.status === 'processing'}
            className="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-text-primary bg-lasomi-primary border border-transparent rounded-md hover:bg-lasomi-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {jobStatus?.status === 'processing' ? (
              <>
                <StopIcon className="w-4 h-4 mr-2" />
                Processing...
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4 mr-2" />
                Run Extraction
              </>
            )}
          </button>

          <button
            disabled={jobStatus?.status !== 'completed'}
            className="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-text-primary bg-lasomi-card border border-border rounded-md hover:bg-lasomi-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <DocumentArrowDownIcon className="w-4 h-4 mr-2" />
            Export Results
          </button>
        </div>
      </div>
    </div>
  );
};

export default function Features() {
  const { logActivity } = useStorage();
  const { 
    state: featuresState, 
    setState: setFeaturesState, 
    loading: sessionLoading 
  } = useAppSession<FeaturesState>('features', defaultState);

  const [aoiState, setAoiState] = useState<AOIDrawingState>(featuresState.aoiState);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(featuresState.jobStatus);
  const [dataSources, setDataSources] = useState(featuresState.dataSources);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [currentDrawingMode, setCurrentDrawingMode] = useState<'polygon' | 'rectangle' | null>(null);

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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      logActivity({
        action: 'upload_design',
        appId: 'features',
        appName: 'Features',
        description: `Uploaded design file: ${file.name}`,
        data: { filename: file.name, size: file.size }
      });
    }
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
        appId: 'features',
        appName: 'Features',
        description: 'Feature extraction completed successfully'
      });
    }, 4000);
  };

  const handleToggleDataSource = async (sourceName: string) => {
    const newSources = {
      ...dataSources,
      [sourceName]: !dataSources[sourceName]
    };
    setDataSources(newSources);

    await logActivity({
      action: 'toggle_source',
      appId: 'features',
      appName: 'Features',
      description: `${newSources[sourceName] ? 'Enabled' : 'Disabled'} ${sourceName}`,
      data: { source: sourceName, enabled: newSources[sourceName] }
    });
  };

  const handleAreaDrawn = (area: any) => {
    setAoiState(prev => ({
      ...prev,
      currentAOI: area,
      isDrawing: false,
      drawingMode: null
    }));
    setCurrentDrawingMode(null);
  };

  const handleDrawingStateChange = (isDrawing: boolean) => {
    if (!isDrawing) {
      setCurrentDrawingMode(null);
    }
  };

  return (
    <div className="flex h-full bg-lasomi-page p-8 gap-8">
      {/* Control Panel */}
      <AOIPanel 
        aoiState={aoiState}
        jobStatus={jobStatus}
        dataSources={dataSources}
        uploadedFile={uploadedFile}
        onFileUpload={handleFileUpload}
        onRunExtraction={handleRunExtraction}
        onToggleDataSource={handleToggleDataSource}
      />

      {/* Map Area */}
      <div className="flex-1">
        <MapComponent 
          drawingMode={currentDrawingMode}
          onDrawingStateChange={handleDrawingStateChange}
          onAreaDrawn={handleAreaDrawn}
        />
      </div>
    </div>
  );
}