import { 
  BuildingLibraryIcon,
  SignalIcon,
  WifiIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

export default function FTTB() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <BuildingLibraryIcon className="w-8 h-8 text-orange-500" />
            <h1 className="text-2xl font-bold text-text-primary">FTTB Design</h1>
          </div>
          <p className="text-text-secondary">
            Design and optimize Fiber to the Building networks for commercial and multi-tenant residential buildings.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <SignalIcon className="w-8 h-8 text-orange-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Network Topology</h3>
            <p className="text-sm text-text-secondary">
              Design optimal fiber network topologies for building connections.
            </p>
          </div>

          <div className="card p-6">
            <WifiIcon className="w-8 h-8 text-orange-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Cable Routing</h3>
            <p className="text-sm text-text-secondary">
              Plan efficient cable routes and distribution points.
            </p>
          </div>

          <div className="card p-6">
            <ChartBarIcon className="w-8 h-8 text-orange-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Capacity Planning</h3>
            <p className="text-sm text-text-secondary">
              Calculate bandwidth requirements and equipment needs.
            </p>
          </div>
        </div>

        {/* Coming soon message */}
        <div className="card p-8 text-center">
          <BuildingLibraryIcon className="w-16 h-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Coming Soon</h2>
          <p className="text-text-secondary">
            Comprehensive FTTB design and planning tools are under development.
          </p>
        </div>
      </div>
    </div>
  );
}
