import { useState, useEffect, useCallback } from 'react';
import { db, ActivityLog, StoredProject } from '@/react-app/lib/storage/database';
import { LocalStorageManager, STORAGE_KEYS } from '@/react-app/lib/storage/localStorage';

// Hook for managing activity logs
export function useActivityLogs(limit: number = 50) {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  const loadActivities = useCallback(async () => {
    try {
      const logs = await db.getRecentActivity(limit);
      setActivities(logs);
    } catch (error) {
      console.error('Failed to load activity logs:', error);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  const logActivity = useCallback(async (activity: Omit<ActivityLog, 'id' | 'timestamp'>) => {
    try {
      await db.logActivity(activity);
      // Reload activities to show the new one
      await loadActivities();
    } catch (error) {
      console.error('Failed to log activity:', error);
    }
  }, [loadActivities]);

  const clearActivities = useCallback(async () => {
    try {
      await db.activityLogs.clear();
      setActivities([]);
    } catch (error) {
      console.error('Failed to clear activities:', error);
    }
  }, []);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  return {
    activities,
    loading,
    logActivity,
    clearActivities,
    reload: loadActivities
  };
}

// Hook for managing app-specific activity logs
export function useAppActivityLogs(appId: string, limit: number = 20) {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  const loadActivities = useCallback(async () => {
    try {
      const logs = await db.getAppActivity(appId, limit);
      setActivities(logs);
    } catch (error) {
      console.error('Failed to load app activity logs:', error);
    } finally {
      setLoading(false);
    }
  }, [appId, limit]);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  return {
    activities,
    loading,
    reload: loadActivities
  };
}

// Hook for managing stored projects
export function useStoredProjects() {
  const [projects, setProjects] = useState<StoredProject[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProjects = useCallback(async () => {
    try {
      const allProjects = await db.projects.orderBy('lastModified').reverse().toArray();
      setProjects(allProjects);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const saveProject = useCallback(async (project: Omit<StoredProject, 'created' | 'lastModified'>) => {
    try {
      await db.projects.put({
        ...project,
        created: new Date(),
        lastModified: new Date()
      });
      await loadProjects();
    } catch (error) {
      console.error('Failed to save project:', error);
    }
  }, [loadProjects]);

  const deleteProject = useCallback(async (projectId: string) => {
    try {
      await db.projects.delete(projectId);
      await loadProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  }, [loadProjects]);

  const getProject = useCallback(async (projectId: string): Promise<StoredProject | undefined> => {
    try {
      return await db.projects.get(projectId);
    } catch (error) {
      console.error('Failed to get project:', error);
      return undefined;
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  return {
    projects,
    loading,
    saveProject,
    deleteProject,
    getProject,
    reload: loadProjects
  };
}

// Hook for managing preferences with localStorage fallback
export function usePreferences<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(defaultValue);
  const [loading, setLoading] = useState(true);

  // Load preference on mount
  useEffect(() => {
    const loadPreference = async () => {
      try {
        // Try IndexedDB first for complex preferences
        const dbValue = await db.getPreferences(key);
        if (dbValue !== null) {
          setValue(dbValue as T);
          setLoading(false);
          return;
        }

        // Fallback to localStorage for simple preferences
        const storageKey = `${STORAGE_KEYS.DESIGNER_SETTINGS}_${key}`;
        const localValue = LocalStorageManager.get(storageKey, defaultValue);
        setValue(localValue);
      } catch (error) {
        console.error('Failed to load preference:', error);
        setValue(defaultValue);
      } finally {
        setLoading(false);
      }
    };

    loadPreference();
  }, [key, defaultValue]);

  // Save preference function
  const savePreference = useCallback(async (newValue: T) => {
    try {
      setValue(newValue);
      
      // Save to IndexedDB for complex data
      if (typeof newValue === 'object' && newValue !== null) {
        await db.savePreferences(key, newValue as Record<string, any>);
      } else {
        // Save to localStorage for simple data
        const storageKey = `${STORAGE_KEYS.DESIGNER_SETTINGS}_${key}`;
        LocalStorageManager.set(storageKey, newValue);
      }
    } catch (error) {
      console.error('Failed to save preference:', error);
    }
  }, [key]);

  return {
    value,
    setValue: savePreference,
    loading
  };
}

// Hook for managing app session state
export function useAppSession<T>(appId: string, defaultState: T) {
  const [state, setState] = useState<T>(defaultState);
  const [loading, setLoading] = useState(true);

  // Load session state on mount
  useEffect(() => {
    const loadSession = async () => {
      try {
        const sessionState = await db.getSession(appId);
        if (sessionState !== null) {
          setState(sessionState);
        }
      } catch (error) {
        console.error('Failed to load session state:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, [appId]);

  // Save session state function
  const saveSession = useCallback(async (newState: T) => {
    try {
      setState(newState);
      await db.saveSession(appId, newState);
    } catch (error) {
      console.error('Failed to save session state:', error);
    }
  }, [appId]);

  // Clear session
  const clearSession = useCallback(async () => {
    try {
      setState(defaultState);
      await db.sessions.delete(appId);
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  }, [appId, defaultState]);

  return {
    state,
    setState: saveSession,
    clearSession,
    loading
  };
}

// Hook for managing localStorage values with React state
export function useLocalStorage<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(() => {
    return LocalStorageManager.get(key, defaultValue);
  });

  const setStoredValue = useCallback((newValue: T) => {
    setValue(newValue);
    LocalStorageManager.set(key, newValue);
  }, [key]);

  return [value, setStoredValue] as const;
}

// Hook for storage information and management
export function useStorageInfo() {
  const [info, setInfo] = useState({
    localStorage: LocalStorageManager.getStorageInfo(),
    indexedDB: { available: true, used: 0, total: 0 }
  });

  const refreshInfo = useCallback(() => {
    setInfo({
      localStorage: LocalStorageManager.getStorageInfo(),
      indexedDB: { available: true, used: 0, total: 0 } // TODO: Implement IndexedDB size calculation
    });
  }, []);

  const exportAllData = useCallback(async () => {
    try {
      const [localStorageData, indexedDBData] = await Promise.all([
        LocalStorageManager.exportData(),
        db.exportData()
      ]);

      return {
        version: 1,
        exportDate: new Date().toISOString(),
        localStorage: localStorageData,
        indexedDB: indexedDBData
      };
    } catch (error) {
      console.error('Failed to export data:', error);
      throw error;
    }
  }, []);

  const clearAllData = useCallback(async () => {
    try {
      LocalStorageManager.clear();
      await db.clearAllData();
      refreshInfo();
    } catch (error) {
      console.error('Failed to clear all data:', error);
      throw error;
    }
  }, [refreshInfo]);

  useEffect(() => {
    refreshInfo();
  }, [refreshInfo]);

  return {
    info,
    refreshInfo,
    exportAllData,
    clearAllData
  };
}
