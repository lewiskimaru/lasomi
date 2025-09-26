import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { Link } from 'react-router';
import { 
  ArrowLeftIcon,
  Cog8ToothIcon,
  UserCircleIcon 
} from '@heroicons/react/24/outline';
import { useStorage } from '@/react-app/context/StorageContext';

interface AppLayoutProps {
  children: React.ReactNode;
  appName: string;
  appDescription?: string;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ 
  children, 
  appName,
  appDescription
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
        <header className="bg-lasomi-sidebar border-b border-border">
          <div className="flex items-center justify-between h-16 px-6">
            {/* Left section - Back button and app info */}
            <div className="flex items-center gap-4">
              <Link
                to="/"
                className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-lg transition-colors"
                title="Back to Dashboard"
              >
                <ArrowLeftIcon className="w-5 h-5" />
              </Link>
              
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-md flex items-center justify-center">
                  <img 
                    src="https://mocha-cdn.com/019985a9-8d62-7868-8c28-6155548128b7/asomi.svg" 
                    alt="Lasomi" 
                    className="w-8 h-8"
                  />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-text-primary">{appName}</h1>
                  {appDescription && (
                    <p className="text-xs text-text-secondary">{appDescription}</p>
                  )}
                </div>
              </div>
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
        position="top-right"
        toastOptions={{
          duration: 4000,
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
