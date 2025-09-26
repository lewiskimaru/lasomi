import { 
  CpuChipIcon,
  EyeIcon,
  MapIcon,
  CloudArrowDownIcon
} from '@heroicons/react/24/outline';

export default function FeatureExtraction() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <CpuChipIcon className="w-8 h-8 text-purple-500" />
            <h1 className="text-2xl font-bold text-text-primary">Feature Extraction</h1>
          </div>
          <p className="text-text-secondary">
            Leverage AI and machine learning to automatically detect and extract infrastructure features from satellite and aerial imagery.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <EyeIcon className="w-8 h-8 text-purple-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Building Detection</h3>
            <p className="text-sm text-text-secondary">
              Automatically identify and outline buildings from satellite imagery.
            </p>
          </div>

          <div className="card p-6">
            <MapIcon className="w-8 h-8 text-purple-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Road Network Extraction</h3>
            <p className="text-sm text-text-secondary">
              Extract road networks and transportation infrastructure features.
            </p>
          </div>

          <div className="card p-6">
            <CloudArrowDownIcon className="w-8 h-8 text-purple-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Multi-Source Data</h3>
            <p className="text-sm text-text-secondary">
              Process data from Microsoft Buildings, Google, and OpenStreetMap.
            </p>
          </div>
        </div>

        {/* Coming soon message */}
        <div className="card p-8 text-center">
          <CpuChipIcon className="w-16 h-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Coming Soon</h2>
          <p className="text-text-secondary">
            Advanced AI-powered feature extraction capabilities are under development.
          </p>
        </div>
      </div>
    </div>
  );
}
