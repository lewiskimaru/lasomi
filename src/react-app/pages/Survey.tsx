import { 
  ClipboardDocumentListIcon,
  MapPinIcon,
  CameraIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

export default function Survey() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <ClipboardDocumentListIcon className="w-8 h-8 text-green-500" />
            <h1 className="text-2xl font-bold text-text-primary">Field Survey</h1>
          </div>
          <p className="text-text-secondary">
            Collect field data, validate infrastructure, and document site conditions for your telecom projects.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <MapPinIcon className="w-8 h-8 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">GPS Data Collection</h3>
            <p className="text-sm text-text-secondary">
              Precise location tracking and waypoint recording for field surveys.
            </p>
          </div>

          <div className="card p-6">
            <CameraIcon className="w-8 h-8 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Photo Documentation</h3>
            <p className="text-sm text-text-secondary">
              Capture and organize site photos with automatic GPS tagging.
            </p>
          </div>

          <div className="card p-6">
            <DocumentTextIcon className="w-8 h-8 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Field Reports</h3>
            <p className="text-sm text-text-secondary">
              Generate comprehensive reports from collected field data.
            </p>
          </div>
        </div>

        {/* Coming soon message */}
        <div className="card p-8 text-center">
          <ClipboardDocumentListIcon className="w-16 h-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Coming Soon</h2>
          <p className="text-text-secondary">
            Advanced field survey tools are under development and will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
