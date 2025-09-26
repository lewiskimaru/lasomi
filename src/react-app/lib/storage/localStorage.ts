// localStorage utilities for simple settings and preferences

const STORAGE_PREFIX = 'lasomi_';

// Storage keys
export const STORAGE_KEYS = {
  // UI Preferences
  THEME: `${STORAGE_PREFIX}theme`,
  SIDEBAR_COLLAPSED: `${STORAGE_PREFIX}sidebar_collapsed`,
  LAST_VISITED_APP: `${STORAGE_PREFIX}last_visited_app`,
  
  // App-specific settings
  DESIGNER_SETTINGS: `${STORAGE_PREFIX}designer_settings`,
  SURVEY_SETTINGS: `${STORAGE_PREFIX}survey_settings`,
  EXTRACTION_SETTINGS: `${STORAGE_PREFIX}extraction_settings`,
  FTTB_SETTINGS: `${STORAGE_PREFIX}fttb_settings`,
  FTTH_SETTINGS: `${STORAGE_PREFIX}ftth_settings`,
  ACCESSORIES_SETTINGS: `${STORAGE_PREFIX}accessories_settings`,
  
  // User preferences
  NOTIFICATIONS_ENABLED: `${STORAGE_PREFIX}notifications_enabled`,
  AUTO_SAVE_ENABLED: `${STORAGE_PREFIX}auto_save_enabled`,
  DEFAULT_MAP_LAYER: `${STORAGE_PREFIX}default_map_layer`,
  
  // Welcome and onboarding
  FIRST_VISIT: `${STORAGE_PREFIX}first_visit`,
  ONBOARDING_COMPLETED: `${STORAGE_PREFIX}onboarding_completed`,
  FEATURE_INTRODUCTIONS: `${STORAGE_PREFIX}feature_introductions`,
} as const;

// Generic storage utilities
export class LocalStorageManager {
  private static isAvailable(): boolean {
    try {
      const test = '__localStorage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }

  static get<T>(key: string, defaultValue: T): T {
    if (!this.isAvailable()) {
      console.warn('localStorage not available, using default value');
      return defaultValue;
    }

    try {
      const item = localStorage.getItem(key);
      if (item === null) return defaultValue;
      
      return JSON.parse(item) as T;
    } catch (error) {
      console.warn(`Failed to parse localStorage item "${key}":`, error);
      return defaultValue;
    }
  }

  static set<T>(key: string, value: T): boolean {
    if (!this.isAvailable()) {
      console.warn('localStorage not available, cannot save');
      return false;
    }

    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error(`Failed to save to localStorage "${key}":`, error);
      return false;
    }
  }

  static remove(key: string): boolean {
    if (!this.isAvailable()) {
      return false;
    }

    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(`Failed to remove localStorage item "${key}":`, error);
      return false;
    }
  }

  static clear(): boolean {
    if (!this.isAvailable()) {
      return false;
    }

    try {
      // Only clear Lasomi-related items
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(STORAGE_PREFIX)) {
          localStorage.removeItem(key);
        }
      });
      return true;
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
      return false;
    }
  }

  static getStorageInfo() {
    if (!this.isAvailable()) {
      return { available: false, used: 0, total: 0 };
    }

    let used = 0;
    const keys = Object.keys(localStorage);
    
    keys.forEach(key => {
      if (key.startsWith(STORAGE_PREFIX)) {
        used += (localStorage.getItem(key) || '').length;
      }
    });

    // Estimate total available space (5MB typical limit)
    const total = 5 * 1024 * 1024; // 5MB in bytes

    return {
      available: true,
      used,
      total,
      percentage: (used / total) * 100,
      itemCount: keys.filter(k => k.startsWith(STORAGE_PREFIX)).length
    };
  }

  // Export Lasomi-specific data
  static exportData() {
    if (!this.isAvailable()) {
      return null;
    }

    const data: Record<string, any> = {};
    const keys = Object.keys(localStorage);

    keys.forEach(key => {
      if (key.startsWith(STORAGE_PREFIX)) {
        try {
          data[key] = JSON.parse(localStorage.getItem(key) || 'null');
        } catch {
          data[key] = localStorage.getItem(key);
        }
      }
    });

    return {
      version: 1,
      exportDate: new Date().toISOString(),
      localStorage: data
    };
  }

  // Import Lasomi-specific data
  static importData(importData: any): boolean {
    if (!this.isAvailable() || !importData.localStorage) {
      return false;
    }

    try {
      Object.entries(importData.localStorage).forEach(([key, value]) => {
        if (key.startsWith(STORAGE_PREFIX)) {
          localStorage.setItem(key, JSON.stringify(value));
        }
      });
      return true;
    } catch (error) {
      console.error('Failed to import localStorage data:', error);
      return false;
    }
  }
}

// Convenience functions for common operations
export const getLastVisitedApp = () => 
  LocalStorageManager.get(STORAGE_KEYS.LAST_VISITED_APP, null);

export const setLastVisitedApp = (appId: string) => 
  LocalStorageManager.set(STORAGE_KEYS.LAST_VISITED_APP, appId);

export const isFirstVisit = () => 
  LocalStorageManager.get(STORAGE_KEYS.FIRST_VISIT, true);

export const markFirstVisitComplete = () => 
  LocalStorageManager.set(STORAGE_KEYS.FIRST_VISIT, false);

export const getNotificationsEnabled = () => 
  LocalStorageManager.get(STORAGE_KEYS.NOTIFICATIONS_ENABLED, true);

export const setNotificationsEnabled = (enabled: boolean) => 
  LocalStorageManager.set(STORAGE_KEYS.NOTIFICATIONS_ENABLED, enabled);

export const getAutoSaveEnabled = () => 
  LocalStorageManager.get(STORAGE_KEYS.AUTO_SAVE_ENABLED, true);

export const setAutoSaveEnabled = (enabled: boolean) => 
  LocalStorageManager.set(STORAGE_KEYS.AUTO_SAVE_ENABLED, enabled);
