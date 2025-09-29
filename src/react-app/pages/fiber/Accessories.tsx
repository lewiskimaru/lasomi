import { 
  WrenchScrewdriverIcon,
  CubeIcon,
  ClipboardDocumentCheckIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';

export default function Accessories() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <WrenchScrewdriverIcon className="w-8 h-8 text-red-500" />
            <h1 className="text-2xl font-bold text-text-primary">Accessories Management</h1>
          </div>
          <p className="text-text-secondary">
            Manage network equipment, hardware accessories, and material requirements for your telecom infrastructure projects.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <CubeIcon className="w-8 h-8 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Equipment Catalog</h3>
            <p className="text-sm text-text-secondary">
              Comprehensive catalog of fiber optic equipment and accessories.
            </p>
          </div>

          <div className="card p-6">
            <ClipboardDocumentCheckIcon className="w-8 h-8 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Bill of Materials</h3>
            <p className="text-sm text-text-secondary">
              Automatically generate detailed BOMs for your network designs.
            </p>
          </div>

          <div className="card p-6">
            <BanknotesIcon className="w-8 h-8 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Cost Estimation</h3>
            <p className="text-sm text-text-secondary">
              Calculate material costs and project budgets accurately.
            </p>
          </div>
        </div>

        {/* Coming soon message */}
        <div className="card p-8 text-center">
          <WrenchScrewdriverIcon className="w-16 h-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Coming Soon</h2>
          <p className="text-text-secondary">
            Advanced accessories and equipment management tools are under development.
          </p>
        </div>
      </div>
    </div>
  );
}
