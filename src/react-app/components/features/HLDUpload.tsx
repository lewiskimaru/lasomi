import React, { useState, useCallback } from 'react';
import { Upload, FileText, X, CheckCircle2, Settings } from 'lucide-react';
import { TreeView, TreeNode } from '@/react-app/components/ui';
import { cn } from '@/react-app/lib/utils';
import HLDUploadSettings, { HLDUploadSettingsData } from './HLDUploadSettings';

export interface UploadedDesign {
  file: File;
  layers: TreeNode[];
  processed: boolean;
}

interface HLDUploadProps {
  onFileUpload: (file: File) => void;
  uploadedDesign: UploadedDesign | null;
  onRemoveFile: () => void;
  onLayerToggle: (nodeId: string) => void;
  settings?: HLDUploadSettingsData;
  onSettingsChange?: (settings: HLDUploadSettingsData) => void;
  className?: string;
}

const HLDUpload: React.FC<HLDUploadProps> = ({
  onFileUpload,
  uploadedDesign,
  onRemoveFile,
  onLayerToggle,
  settings,
  onSettingsChange,
  className
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const validFile = files.find(file => 
      /\.(kmz|kml|geojson|csv)$/i.test(file.name)
    );
    
    if (validFile) {
      onFileUpload(validFile);
    }
  }, [onFileUpload]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
    // Reset input value to allow re-selecting the same file
    e.target.value = '';
  }, [onFileUpload]);

  const getSupportedFormats = () => ['KMZ', 'KML', 'GeoJSON', 'CSV'];
  
  const getFileIcon = () => {
    return <FileText className="w-4 h-4" />;
  };

  const truncateFilename = (filename: string, maxLength: number = 25) => {
    if (filename.length <= maxLength) return filename;
    const ext = filename.split('.').pop();
    const nameWithoutExt = filename.slice(0, filename.lastIndexOf('.'));
    const truncatedName = nameWithoutExt.slice(0, maxLength - ext!.length - 4) + '...';
    return `${truncatedName}.${ext}`;
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Upload Section */}
      {!uploadedDesign && (
        <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-md p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-text-primary">HLD Upload</h3>
            {settings && onSettingsChange && (
              <button
                onClick={() => setShowSettings(true)}
                className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary/30 rounded border border-border/30 hover:border-border/60 transition-all duration-200"
                title="Upload Settings"
              >
                <Settings className="w-4 h-4" />
              </button>
            )}
          </div>
          
          <div
            className={cn(
              "relative border-2 border-dashed rounded-lg p-6 transition-all duration-200 cursor-pointer",
              isDragOver 
                ? "border-lasomi-primary bg-lasomi-primary/10" 
                : "border-border bg-lasomi-secondary/30 hover:bg-lasomi-secondary/50"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('hld-file-input')?.click()}
          >
            <input
              id="hld-file-input"
              type="file"
              accept=".kmz,.kml,.geojson,.csv"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="flex flex-col items-center justify-center space-y-3">
              <Upload className={cn(
                "w-8 h-8 transition-colors",
                isDragOver ? "text-lasomi-primary" : "text-text-secondary"
              )} />
              
              <div className="text-center">
                <p className="text-sm font-medium text-text-primary">
                  {isDragOver ? "Drop your HLD file here" : "Drop HLD file or click to browse"}
                </p>
                <p className="text-xs text-text-secondary mt-1">
                  Supported formats: {getSupportedFormats().join(', ')}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Uploaded File Display with Tree View */}
      {uploadedDesign && (
        <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-md p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-text-primary">HLD Upload</h3>
            <div className="flex items-center space-x-1">
              {settings && onSettingsChange && (
                <button
                  onClick={() => setShowSettings(true)}
                  className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary/30 rounded border border-border/30 hover:border-border/60 transition-all duration-200"
                  title="Upload Settings"
                >
                  <Settings className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={onRemoveFile}
                className="p-1.5 text-text-secondary hover:text-red-500 hover:bg-red-50 rounded border border-border/30 hover:border-red-200 transition-all duration-200"
                title="Remove file"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* File Info */}
          <div className="flex items-center space-x-3 mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                {getFileIcon()}
                <span className="text-sm font-medium text-text-primary" title={uploadedDesign.file.name}>
                  {truncateFilename(uploadedDesign.file.name)}
                </span>
              </div>
              <p className="text-xs text-text-secondary">
                {(uploadedDesign.file.size / 1024 / 1024).toFixed(2)} MB • 
                {uploadedDesign.processed ? ' Processed' : ' Processing...'}
              </p>
            </div>
          </div>

          {/* Layers Tree View */}
          {uploadedDesign.layers.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-gray-700">Design Layers</label>
                <span className="text-xs text-gray-500">
                  {uploadedDesign.layers.reduce((count, layer) => count + (layer.children?.length || 0), 0)} items
                </span>
              </div>
              
              <TreeView
                data={uploadedDesign.layers}
                onNodeClick={(node) => onLayerToggle(node.id)}
                defaultExpandedIds={[uploadedDesign.layers[0]?.id]}
                className="max-h-64 overflow-y-auto border-0 bg-gray-50"
                showLines={true}
                animateExpand={true}
                indent={16}
              />
            </div>
          )}

          {/* Replace File Button */}
          <div className="mt-4 pt-3 border-t border-gray-200">
            <button
              onClick={() => document.getElementById('hld-file-input-replace')?.click()}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Upload different file
            </button>
            <input
              id="hld-file-input-replace"
              type="file"
              accept=".kmz,.kml,.geojson,.csv"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {settings && onSettingsChange && (
        <HLDUploadSettings
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          settings={settings}
          onSettingsChange={onSettingsChange}
        />
      )}
    </div>
  );
};

export default HLDUpload;