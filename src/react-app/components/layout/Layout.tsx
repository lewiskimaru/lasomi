import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
  projectName?: string;
}

export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  showSidebar = true,
  projectName 
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleSearch = (query: string) => {
    console.log('Search:', query);
    // TODO: Implement search functionality
  };

  const handleSettings = () => {
    console.log('Settings clicked');
    // TODO: Open settings modal
  };

  const handleNotifications = () => {
    console.log('Notifications clicked');
    // TODO: Open notifications panel
  };

  const handleProfile = () => {
    console.log('Profile clicked');
    // TODO: Open profile menu
  };

  return (
    <div className="flex h-screen bg-lasomi-page">
      {/* Sidebar */}
      {showSidebar && (
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      )}

      {/* Main content area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar */}
        <TopBar
          projectName={projectName}
          onSearch={handleSearch}
          onSettingsClick={handleSettings}
          onNotificationsClick={handleNotifications}
          onProfileClick={handleProfile}
        />

        {/* Main content */}
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
