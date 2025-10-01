import React, { useState } from 'react';
import { X, Settings } from 'lucide-react';

export interface HLDUploadSettingsData {
  defaultDataSources: {
    buildingFootprints: 'google' | 'osm' | 'microsoft';
    roadNetworks: 'osm' | 'google';
    placeNames: 'google' | 'osm';
  };
  qualitySettings: {
    buildingConfidence: number;
    minBuildingSize: number;
    roadClassification: {
      primary: boolean;
      secondary: boolean;
      residential: boolean;
      footpaths: boolean;
    };
  };
  processing: {
    autoProcess: boolean;
    enableNotifications: boolean;
  };
}

interface HLDUploadSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: HLDUploadSettingsData;
  onSettingsChange: (settings: HLDUploadSettingsData) => void;
}

const HLDUploadSettings: React.FC<HLDUploadSettingsProps> = ({
  isOpen,
  onClose,
  settings,
  onSettingsChange
}) => {
  const [localSettings, setLocalSettings] = useState<HLDUploadSettingsData>(settings);

  const handleSave = () => {
    onSettingsChange(localSettings);
    onClose();
  };

  const handleCancel = () => {
    setLocalSettings(settings); // Reset to original settings
    onClose();
  };

  const updateDataSource = (category: keyof HLDUploadSettingsData['defaultDataSources'], value: string) => {
    setLocalSettings(prev => ({
      ...prev,
      defaultDataSources: {
        ...prev.defaultDataSources,
        [category]: value
      }
    }));
  };

  const updateQualitySetting = (key: string, value: any) => {
    setLocalSettings(prev => ({
      ...prev,
      qualitySettings: {
        ...prev.qualitySettings,
        [key]: value
      }
    }));
  };

  const updateRoadClassification = (road: string, enabled: boolean) => {
    setLocalSettings(prev => ({
      ...prev,
      qualitySettings: {
        ...prev.qualitySettings,
        roadClassification: {
          ...prev.qualitySettings.roadClassification,
          [road]: enabled
        }
      }
    }));
  };

  const updateProcessingSetting = (key: keyof HLDUploadSettingsData['processing'], value: boolean) => {
    setLocalSettings(prev => ({
      ...prev,
      processing: {
        ...prev.processing,
        [key]: value
      }
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-lg w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-text-secondary" />
            <h2 className="text-lg font-semibold text-text-primary">HLD Upload Settings</h2>
          </div>
          <button
            onClick={handleCancel}
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="space-y-6">
            {/* Default Data Sources */}
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-4">Default Data Sources</h3>
              <div className="space-y-4">
                {/* Building Footprints */}
                <div>
                  <label className="block text-xs font-medium text-text-primary mb-2">
                    Building Footprints
                  </label>
                  <select
                    value={localSettings.defaultDataSources.buildingFootprints}
                    onChange={(e) => updateDataSource('buildingFootprints', e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-border rounded-md bg-lasomi-card text-text-primary focus:ring-2 focus:ring-lasomi-primary focus:border-transparent"
                  >
                    <option value="google">Google Buildings</option>
                    <option value="microsoft">Microsoft Buildings</option>
                    <option value="osm">OpenStreetMap Buildings</option>
                  </select>
                </div>

                {/* Road Networks */}
                <div>
                  <label className="block text-xs font-medium text-text-primary mb-2">
                    Road Networks
                  </label>
                  <select
                    value={localSettings.defaultDataSources.roadNetworks}
                    onChange={(e) => updateDataSource('roadNetworks', e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-border rounded-md bg-lasomi-card text-text-primary focus:ring-2 focus:ring-lasomi-primary focus:border-transparent"
                  >
                    <option value="osm">OpenStreetMap Roads</option>
                    <option value="google">Google Roads</option>
                  </select>
                </div>

                {/* Place Names */}
                <div>
                  <label className="block text-xs font-medium text-text-primary mb-2">
                    Place Names
                  </label>
                  <select
                    value={localSettings.defaultDataSources.placeNames}
                    onChange={(e) => updateDataSource('placeNames', e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-border rounded-md bg-lasomi-card text-text-primary focus:ring-2 focus:ring-lasomi-primary focus:border-transparent"
                  >
                    <option value="google">Google Places API</option>
                    <option value="osm">OpenStreetMap POIs</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Quality Settings */}
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-4">Quality Settings</h3>
              <div className="space-y-4">
                {/* Building Confidence */}
                <div>
                  <label className="block text-xs font-medium text-text-primary mb-2">
                    Building Confidence: {localSettings.qualitySettings.buildingConfidence}%
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="100"
                    step="5"
                    value={localSettings.qualitySettings.buildingConfidence}
                    onChange={(e) => updateQualitySetting('buildingConfidence', parseInt(e.target.value))}
                    className="w-full h-2 bg-lasomi-secondary rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-text-secondary mt-1">
                    <span>50%</span>
                    <span>100%</span>
                  </div>
                </div>

                {/* Min Building Size */}
                <div>
                  <label className="block text-xs font-medium text-text-primary mb-2">
                    Minimum Building Size (m²)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="100"
                    value={localSettings.qualitySettings.minBuildingSize}
                    onChange={(e) => updateQualitySetting('minBuildingSize', parseInt(e.target.value))}
                    className="w-full px-3 py-2 text-sm border border-border rounded-md bg-lasomi-card text-text-primary focus:ring-2 focus:ring-lasomi-primary focus:border-transparent"
                  />
                </div>

                {/* Road Classification */}
                <div>
                  <label className="block text-xs font-medium text-text-primary mb-2">
                    Road Classification
                  </label>
                  <div className="space-y-2">
                    {Object.entries(localSettings.qualitySettings.roadClassification).map(([road, enabled]) => (
                      <label key={road} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={enabled}
                          onChange={(e) => updateRoadClassification(road, e.target.checked)}
                          className="h-3 w-3 text-lasomi-primary border-border rounded focus:ring-lasomi-primary bg-lasomi-card"
                        />
                        <span className="ml-2 text-xs text-text-primary capitalize">
                          {road.replace(/([A-Z])/g, ' $1').trim()}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Processing Settings */}
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-4">Processing</h3>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={localSettings.processing.autoProcess}
                    onChange={(e) => updateProcessingSetting('autoProcess', e.target.checked)}
                    className="h-3 w-3 text-lasomi-primary border-border rounded focus:ring-lasomi-primary bg-lasomi-card"
                  />
                  <span className="ml-2 text-xs text-text-primary">
                    Auto-process after file upload
                  </span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={localSettings.processing.enableNotifications}
                    onChange={(e) => updateProcessingSetting('enableNotifications', e.target.checked)}
                    className="h-3 w-3 text-lasomi-primary border-border rounded focus:ring-lasomi-primary bg-lasomi-card"
                  />
                  <span className="ml-2 text-xs text-text-primary">
                    Enable processing notifications
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-border bg-lasomi-secondary/20">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-lasomi-primary hover:bg-lasomi-primary/80 rounded-md transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default HLDUploadSettings;