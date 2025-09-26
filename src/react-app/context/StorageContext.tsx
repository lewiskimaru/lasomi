import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useActivityLogs, useStoredProjects, useLocalStorage } from '@/react-app/hooks/useStorage';
import { setLastVisitedApp, markFirstVisitComplete } from '@/react-app/lib/storage/localStorage';
import { ActivityLog, StoredProject } from '@/react-app/lib/storage/database';

interface StorageContextType {
  // Activity tracking
  activities: ActivityLog[];
  activitiesLoading: boolean;
  logActivity: (activity: Omit<ActivityLog, 'id' | 'timestamp'>) => Promise<void>;
  clearActivities: () => Promise<void>;
  
  // Project management
  projects: StoredProject[];
  projectsLoading: boolean;
  saveProject: (project: Omit<StoredProject, 'created' | 'lastModified'>) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  getProject: (projectId: string) => Promise<StoredProject | undefined>;
  
  // User preferences
  lastVisitedApp: string | null;
  setLastVisitedApp: (appId: string) => void;
  notificationsEnabled: boolean;
  setNotificationsEnabled: (enabled: boolean) => void;
  autoSaveEnabled: boolean;
  setAutoSaveEnabled: (enabled: boolean) => void;
  
  // App state
  firstVisit: boolean;
  markFirstVisitComplete: () => void;
}

const StorageContext = createContext<StorageContextType | null>(null);

interface StorageProviderProps {
  children: ReactNode;
}

export const StorageProvider: React.FC<StorageProviderProps> = ({ children }) => {
  // Activity logs
  const {
    activities,
    loading: activitiesLoading,
    logActivity,
    clearActivities
  } = useActivityLogs();

  // Projects
  const {
    projects,
    loading: projectsLoading,
    saveProject,
    deleteProject,
    getProject
  } = useStoredProjects();

  // User preferences
  const [lastVisitedApp, setLastVisitedAppState] = useLocalStorage<string | null>('lasomi_last_visited_app', null);
  const [notificationsEnabled, setNotificationsEnabled] = useLocalStorage('lasomi_notifications_enabled', true);
  const [autoSaveEnabled, setAutoSaveEnabled] = useLocalStorage('lasomi_auto_save_enabled', true);
  const [firstVisit, setFirstVisit] = useLocalStorage('lasomi_first_visit', true);

  // Enhanced setLastVisitedApp that also tracks activity
  const handleSetLastVisitedApp = async (appId: string) => {
    setLastVisitedAppState(appId);
    setLastVisitedApp(appId);
    
    // Log app visit activity
    await logActivity({
      action: 'app_visit',
      appId,
      appName: getAppName(appId),
      description: `Opened ${getAppName(appId)} app`
    });
  };

  const handleMarkFirstVisitComplete = () => {
    setFirstVisit(false);
    markFirstVisitComplete();
  };

  // Track app navigation and log activity
  useEffect(() => {
    const handleRouteChange = () => {
      const path = window.location.pathname;
      const appMatch = path.match(/\/app\/(\w+)/);
      
      if (appMatch) {
        const appId = appMatch[1];
        handleSetLastVisitedApp(appId);
      }
    };

    // Listen for navigation changes
    window.addEventListener('popstate', handleRouteChange);
    
    // Check current route on mount
    handleRouteChange();

    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, []);

  // Log first visit
  useEffect(() => {
    if (firstVisit) {
      logActivity({
        action: 'first_visit',
        appId: 'dashboard',
        appName: 'Dashboard',
        description: 'First time visiting Lasomi'
      });
    }
  }, [firstVisit, logActivity]);

  const contextValue: StorageContextType = {
    // Activity tracking
    activities,
    activitiesLoading,
    logActivity,
    clearActivities,
    
    // Project management
    projects,
    projectsLoading,
    saveProject,
    deleteProject,
    getProject,
    
    // User preferences
    lastVisitedApp,
    setLastVisitedApp: handleSetLastVisitedApp,
    notificationsEnabled,
    setNotificationsEnabled,
    autoSaveEnabled,
    setAutoSaveEnabled,
    
    // App state
    firstVisit,
    markFirstVisitComplete: handleMarkFirstVisitComplete
  };

  return (
    <StorageContext.Provider value={contextValue}>
      {children}
    </StorageContext.Provider>
  );
};

export const useStorage = (): StorageContextType => {
  const context = useContext(StorageContext);
  if (!context) {
    throw new Error('useStorage must be used within a StorageProvider');
  }
  return context;
};

// Helper function to get app display name
function getAppName(appId: string): string {
  const appNames: Record<string, string> = {
    'designer': 'Designer',
    'survey': 'Survey',
    'extraction': 'Feature Extraction',
    'fttb': 'FTTB',
    'ftth': 'FTTH',
    'accessories': 'Accessories',
    'dashboard': 'Dashboard'
  };
  
  return appNames[appId] || appId;
}
