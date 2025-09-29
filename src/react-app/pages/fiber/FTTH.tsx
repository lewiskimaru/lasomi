import { 
  HomeModernIcon,
  MapIcon,
  UsersIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

export default function FTTH() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <HomeModernIcon className="w-8 h-8 text-teal-500" />
            <h1 className="text-2xl font-bold text-text-primary">FTTH Planning</h1>
          </div>
          <p className="text-text-secondary">
            Plan and design Fiber to the Home networks for residential areas with optimized coverage and cost efficiency.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <MapIcon className="w-8 h-8 text-teal-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Service Area Planning</h3>
            <p className="text-sm text-text-secondary">
              Define optimal service areas and coverage zones for residential fiber.
            </p>
          </div>

          <div className="card p-6">
            <UsersIcon className="w-8 h-8 text-teal-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Customer Clustering</h3>
            <p className="text-sm text-text-secondary">
              Group customers efficiently for splitter and distribution point placement.
            </p>
          </div>

          <div className="card p-6">
            <CurrencyDollarIcon className="w-8 h-8 text-teal-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Cost Optimization</h3>
            <p className="text-sm text-text-secondary">
              Minimize deployment costs while maximizing service quality.
            </p>
          </div>
        </div>

        {/* Coming soon message */}
        <div className="card p-8 text-center">
          <HomeModernIcon className="w-16 h-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Coming Soon</h2>
          <p className="text-text-secondary">
            Advanced FTTH planning and optimization tools are under development.
          </p>
        </div>
      </div>
    </div>
  );
}
