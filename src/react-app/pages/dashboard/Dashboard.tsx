import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  MapIcon,
  ClipboardDocumentListIcon,
  CpuChipIcon,
  BuildingLibraryIcon,
  HomeModernIcon,
  WrenchScrewdriverIcon,
  Cog8ToothIcon,
  ClockIcon,
  DocumentTextIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import { useStorage } from '@/react-app/context/StorageContext';
import { WelcomeMessage } from '@/react-app/components/common/WelcomeMessage';
import { StorageStatus } from '@/react-app/components/common/StorageStatus';

interface AppCard {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  color: string;
}

interface WaffleMenuProps {
  isOpen: boolean;
  onClose: () => void;
  apps: AppCard[];
}

const appCards: AppCard[] = [
  {
    id: 'features',
    title: 'Features',
    description: 'Extract buildings, roads and landmarks',
    icon: CpuChipIcon,
    href: '/features',
    color: 'from-purple-500 to-purple-600'
  },
  {
    id: 'accessories',
    title: 'Accessories',
    description: 'Add Network Accessories',
    icon: WrenchScrewdriverIcon,
    href: '/accessories',
    color: 'from-red-500 to-red-600'
  },
  {
    id: 'ftth',
    title: 'FTTH',
    description: 'Fiber to the home network planning',
    icon: HomeModernIcon,
    href: '/ftth',
    color: 'from-teal-500 to-teal-600'
  },
  {
    id: 'fttb',
    title: 'FTTB',
    description: 'Fiber to the building network design',
    icon: BuildingLibraryIcon,
    href: '/fttb',
    color: 'from-orange-500 to-orange-600'
  },
  {
    id: 'survey',
    title: 'Survey',
    description: 'Field data collection and validation tools',
    icon: ClipboardDocumentListIcon,
    href: '/survey',
    color: 'from-green-500 to-green-600'
  },
  {
    id: 'learn',
    title: 'Learn',
    description: 'Training materials and documentation',
    icon: AcademicCapIcon,
    href: '/learn',
    color: 'from-indigo-500 to-indigo-600'
  }
];

const WaffleMenu: React.FC<WaffleMenuProps> = ({ isOpen, onClose, apps }) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className="absolute top-12 right-0 w-80 bg-lasomi-card border-[10px] border-border rounded-2xl shadow-lasomi-lg z-50 overflow-hidden"
    >
      {/* Scrollable apps section */}
      <div className="max-h-96 overflow-y-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-border">
        <div className="p-4">
          <div className="grid grid-cols-3 gap-4">
            {apps.map((app) => {
              const IconComponent = app.icon;
              return (
                <Link
                  key={app.id}
                  to={app.href}
                  onClick={onClose}
                  className="flex flex-col items-center p-3 rounded-2xl hover:bg-lasomi-secondary transition-colors group"
                >
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${app.color} flex items-center justify-center mb-2 group-hover:scale-110 transition-transform duration-200`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-xs text-text-primary text-center leading-tight">
                    {app.title}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* About Atomio section */}
      <div className="border-t border-border" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
        <div className="p-4">
          <a 
            href="https://www.atomio.tech"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2 px-4 text-sm text-text-secondary hover:text-text-primary hover:bg-border-light border border-border rounded-full transition-colors text-center block"
            onClick={onClose}
          >
            About Atomio
          </a>
        </div>
      </div>
    </div>
  );
}

// Helper function to format time ago
const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
};

interface AppCardComponentProps {
  app: AppCard;
}

const AppCardComponent: React.FC<AppCardComponentProps> = ({ app }) => {
  const IconComponent = app.icon;
  const { logActivity } = useStorage();

  const handleAppClick = async () => {
    await logActivity({
      action: 'app_open',
      appId: app.id,
      appName: app.title,
      description: `Opened ${app.title} app from dashboard`
    });
  };

  return (
    <Link
      to={app.href}
      onClick={handleAppClick}
      className="group relative overflow-hidden bg-lasomi-card border border-border rounded-lg hover:border-border-medium transition-all duration-300 hover:shadow-lasomi-lg"
    >
      <div className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${app.color} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
            <IconComponent className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary group-hover:text-white transition-colors">
              {app.title}
            </h3>
            <p className="text-sm text-text-secondary group-hover:text-text-primary transition-colors">
              {app.description}
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
            Click to open
          </span>
          <div className="w-6 h-6 rounded-full bg-lasomi-secondary group-hover:bg-border-medium flex items-center justify-center transition-colors">
            <svg className="w-3 h-3 text-text-secondary group-hover:text-text-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
      
      {/* Hover effect overlay */}
      <div className={`absolute inset-0 bg-gradient-to-br ${app.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
    </Link>
  );
};

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const { 
    activities, 
    clearActivities, 
    notificationsEnabled, 
    setNotificationsEnabled,
    autoSaveEnabled,
    setAutoSaveEnabled 
  } = useStorage();
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const handleExportData = async () => {
    try {
      // This would export all user data
      const data = {
        activities: activities.slice(0, 100), // Last 100 activities
        settings: {
          notificationsEnabled,
          autoSaveEnabled
        },
        exportDate: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lasomi-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export data:', error);
    }
  };

  const handleClearData = async () => {
    if (showClearConfirm) {
      await clearActivities();
      setShowClearConfirm(false);
    } else {
      setShowClearConfirm(true);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-lg w-full max-w-md">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-text-primary mb-6">Settings</h2>
          
          {/* Preferences */}
          <div className="space-y-4 mb-6">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-text-primary">Notifications</label>
              <button
                onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  notificationsEnabled ? 'bg-lasomi-primary' : 'bg-lasomi-secondary'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${
                    notificationsEnabled ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-text-primary">Auto-save</label>
              <button
                onClick={() => setAutoSaveEnabled(!autoSaveEnabled)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  autoSaveEnabled ? 'bg-lasomi-primary' : 'bg-lasomi-secondary'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${
                    autoSaveEnabled ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Data Management */}
          <div className="space-y-3 mb-6">
            <h3 className="text-sm font-medium text-text-primary">Data Management</h3>
            
            <button
              onClick={handleExportData}
              className="w-full btn btn-secondary justify-start"
            >
              <ArrowDownTrayIcon className="w-4 h-4" />
              Export Data
            </button>
            
            <button
              onClick={handleClearData}
              className={`w-full btn justify-start ${
                showClearConfirm ? 'bg-danger text-white' : 'btn-ghost text-danger'
              }`}
            >
              <TrashIcon className="w-4 h-4" />
              {showClearConfirm ? 'Confirm Clear Data' : 'Clear All Data'}
            </button>
            
            {showClearConfirm && (
              <p className="text-xs text-text-secondary">
                This will permanently delete all your activity history and projects.
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <button
              onClick={onClose}
              className="btn btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [waffleMenuOpen, setWaffleMenuOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const { activities, activitiesLoading, firstVisit, markFirstVisitComplete } = useStorage();

  // Mark first visit as complete after a short delay
  useEffect(() => {
    if (firstVisit) {
      const timer = setTimeout(() => {
        markFirstVisitComplete();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [firstVisit, markFirstVisitComplete]);

  const toggleWaffleMenu = () => {
    setWaffleMenuOpen(!waffleMenuOpen);
  };

  const toggleSettings = () => {
    setSettingsOpen(!settingsOpen);
  };

  return (
    <div className="min-h-screen bg-lasomi-page">
      {/* Header */}
      <header className="bg-lasomi-page border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and title */}
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-text-primary">Lasomi</h1>
            </div>

            {/* User actions */}
            <div className="flex items-center gap-3 relative">
              {/* Settings Button */}
              <button 
                onClick={toggleSettings}
                className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-lg transition-colors"
                title="Settings"
              >
                <Cog8ToothIcon className="w-5 h-5" />
              </button>

              {/* Waffle Menu Button */}
              <button 
                onClick={toggleWaffleMenu}
                className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-lg transition-colors"
                title="Apps"
              >
                <div className="w-5 h-5 grid grid-cols-3 gap-0.5">
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                  <div className="w-1 h-1 bg-current rounded-full"></div>
                </div>
              </button>

              {/* Waffle Menu */}
              <WaffleMenu 
                isOpen={waffleMenuOpen}
                onClose={() => setWaffleMenuOpen(false)}
                apps={appCards}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Welcome message for first-time users */}
        <WelcomeMessage />

        {/* Storage status warning if needed */}
        <StorageStatus className="mb-6" />

        {/* Welcome section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-text-primary mb-4">
            Less tracing. More connecting.
          </h2>
        </div>

        {/* Apps grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {appCards.map((app) => (
            <AppCardComponent key={app.id} app={app} />
          ))}
        </div>

        {/* Recent activity section */}
        <div className="bg-lasomi-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Recent Activity</h3>
          
          {activitiesLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin w-6 h-6 border-2 border-lasomi-primary border-t-transparent rounded-full mx-auto"></div>
              <p className="text-text-secondary mt-2">Loading activity...</p>
            </div>
          ) : activities.length > 0 ? (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {activities.slice(0, 10).map((activity, index) => (
                <div key={activity.id || index} className="flex items-start gap-3 p-3 bg-lasomi-secondary rounded-md">
                  <div className="w-8 h-8 rounded-md bg-lasomi-primary flex items-center justify-center flex-shrink-0">
                    {activity.appId === 'dashboard' ? (
                      <ClipboardDocumentListIcon className="w-4 h-4 text-white" />
                    ) : activity.appId === 'designer' ? (
                      <MapIcon className="w-4 h-4 text-white" />
                    ) : activity.appId === 'survey' ? (
                      <ClipboardDocumentListIcon className="w-4 h-4 text-white" />
                    ) : activity.appId === 'extraction' ? (
                      <CpuChipIcon className="w-4 h-4 text-white" />
                    ) : activity.appId === 'fttb' ? (
                      <BuildingLibraryIcon className="w-4 h-4 text-white" />
                    ) : activity.appId === 'ftth' ? (
                      <HomeModernIcon className="w-4 h-4 text-white" />
                    ) : activity.appId === 'accessories' ? (
                      <WrenchScrewdriverIcon className="w-4 h-4 text-white" />
                    ) : (
                      <DocumentTextIcon className="w-4 h-4 text-white" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary">{activity.description}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-text-secondary">{activity.appName}</span>
                      <span className="text-xs text-text-secondary">•</span>
                      <div className="flex items-center gap-1">
                        <ClockIcon className="w-3 h-3 text-text-secondary" />
                        <span className="text-xs text-text-secondary">
                          {formatTimeAgo(activity.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {activities.length > 10 && (
                <div className="text-center pt-3">
                  <p className="text-xs text-text-secondary">
                    Showing 10 of {activities.length} activities
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <ClipboardDocumentListIcon className="w-12 h-12 text-text-secondary mx-auto mb-4" />
              <p className="text-text-secondary">No recent activity</p>
              <p className="text-sm text-text-secondary mt-2">
                Your recent projects and activities will appear here
              </p>
            </div>
          )}
        </div>

        {/* Settings Modal */}
        <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
      </main>
    </div>
  );
}
