import React, { useEffect } from 'react';
import { Toaster } from 'sonner';
import { Link } from 'react-router-dom';
import { 
  Cog8ToothIcon,
  UserCircleIcon 
} from '@heroicons/react/24/outline';
import { ChevronLeft } from 'lucide-react';
import { useStorage } from '@/react-app/context/StorageContext';

interface AppLayoutProps {
  children: React.ReactNode;
  appName: string;
  appDescription?: string; // Keep for backward compatibility
}

export const AppLayout: React.FC<AppLayoutProps> = ({ 
  children, 
  appName
}) => {
  const { logActivity } = useStorage();

  // Log app entry
  useEffect(() => {
    const appId = window.location.pathname.split('/').pop() || 'unknown';
    logActivity({
      action: 'app_enter',
      appId,
      appName,
      description: `Entered ${appName} app`
    });
  }, [appName, logActivity]);

  return (
    <div className="flex h-screen bg-lasomi-page">
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* App header */}
        <header className="bg-lasomi-page border-b border-border">
          <div className="flex items-center justify-between h-16 px-6">
            {/* Left section - Back button and breadcrumb */}
            <div className="flex items-center gap-4">
              <Link
                to="/"
                className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-lg transition-colors"
                title="Back to Dashboard"
              >
                <ChevronLeft className="w-5 h-5" />
              </Link>
              
              {/* Breadcrumb */}
              <nav className="flex items-center text-2xl font-bold">
                <Link 
                  to="/" 
                  className="text-text-secondary hover:text-text-primary transition-colors"
                >
                  Lasomi
                </Link>
                <span className="mx-2 text-text-secondary">›</span>
                <span className="text-text-primary">{appName}</span>
              </nav>
            </div>

            {/* Right section - User actions */}
            <div className="flex items-center gap-2">
              <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-md transition-colors">
                <Cog8ToothIcon className="w-5 h-5" />
              </button>
              <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-md transition-colors">
                <UserCircleIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* App content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>

      {/* Toast notifications */}
      <Toaster
        position="bottom-right"
        expand={false}
        richColors
        closeButton
        duration={4000}
        toastOptions={{
          style: {
            background: 'var(--card-background)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
          },
        }}
      />
    </div>
  );
};
