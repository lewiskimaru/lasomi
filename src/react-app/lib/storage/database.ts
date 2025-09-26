import Dexie, { Table } from 'dexie';

// Database schema interfaces
export interface StoredProject {
  id: string;
  name: string;
  description?: string;
  type: 'designer' | 'survey' | 'extraction' | 'fttb' | 'ftth' | 'accessories';
  data: any; // Project-specific data
  lastModified: Date;
  created: Date;
}

export interface ActivityLog {
  id?: number;
  action: string;
  appId: string;
  appName: string;
  description: string;
  data?: any;
  timestamp: Date;
}

export interface UserPreferences {
  id: string;
  category: string;
  settings: Record<string, any>;
  lastUpdated: Date;
}

export interface AppSession {
  id: string;
  appId: string;
  state: any;
  lastActive: Date;
}

// Dexie database class
export class LasomoiDB extends Dexie {
  projects!: Table<StoredProject>;
  activityLogs!: Table<ActivityLog>;
  preferences!: Table<UserPreferences>;
  sessions!: Table<AppSession>;

  constructor() {
    super('LasomoiDB');
    
    this.version(1).stores({
      projects: 'id, name, type, lastModified, created',
      activityLogs: '++id, appId, timestamp',
      preferences: 'id, category, lastUpdated',
      sessions: 'id, appId, lastActive'
    });

    // Hooks for automatic timestamp updates
    this.projects.hook('creating', (_primKey, obj, _trans) => {
      obj.created = new Date();
      obj.lastModified = new Date();
    });

    this.projects.hook('updating', (modifications, _primKey, _obj, _trans) => {
      (modifications as any).lastModified = new Date();
    });

    this.activityLogs.hook('creating', (_primKey, obj, _trans) => {
      obj.timestamp = new Date();
    });

    this.preferences.hook('creating', (_primKey, obj, _trans) => {
      obj.lastUpdated = new Date();
    });

    this.preferences.hook('updating', (modifications, _primKey, _obj, _trans) => {
      (modifications as any).lastUpdated = new Date();
    });

    this.sessions.hook('creating', (_primKey, obj, _trans) => {
      obj.lastActive = new Date();
    });

    this.sessions.hook('updating', (modifications, _primKey, _obj, _trans) => {
      (modifications as any).lastActive = new Date();
    });
  }

  // Cleanup old activity logs (keep last 1000 entries)
  async cleanupActivityLogs() {
    const count = await this.activityLogs.count();
    if (count > 1000) {
      const oldestEntries = await this.activityLogs
        .orderBy('timestamp')
        .limit(count - 1000)
        .toArray();
      
      const idsToDelete = oldestEntries.map(entry => entry.id!);
      await this.activityLogs.bulkDelete(idsToDelete);
    }
  }

  // Get recent activity with limit
  async getRecentActivity(limit: number = 50): Promise<ActivityLog[]> {
    return await this.activityLogs
      .orderBy('timestamp')
      .reverse()
      .limit(limit)
      .toArray();
  }

  // Get activity for specific app
  async getAppActivity(appId: string, limit: number = 20): Promise<ActivityLog[]> {
    return await this.activityLogs
      .where('appId')
      .equals(appId)
      .reverse()
      .sortBy('timestamp')
      .then(results => results.slice(0, limit));
  }

  // Add activity log entry
  async logActivity(activity: Omit<ActivityLog, 'id' | 'timestamp'>) {
    await this.activityLogs.add({
      ...activity,
      timestamp: new Date()
    });
    
    // Cleanup if needed (don't await to avoid blocking)
    this.cleanupActivityLogs().catch(console.warn);
  }

  // Get preferences by category
  async getPreferences(category: string): Promise<Record<string, any> | null> {
    const pref = await this.preferences.get(category);
    return pref?.settings || null;
  }

  // Save preferences
  async savePreferences(category: string, settings: Record<string, any>) {
    await this.preferences.put({
      id: category,
      category,
      settings,
      lastUpdated: new Date()
    });
  }

  // Get or create app session
  async getSession(appId: string): Promise<any | null> {
    const session = await this.sessions.get(appId);
    return session?.state || null;
  }

  // Save app session
  async saveSession(appId: string, state: any) {
    await this.sessions.put({
      id: appId,
      appId,
      state,
      lastActive: new Date()
    });
  }

  // Export data for backup
  async exportData() {
    const [projects, activityLogs, preferences, sessions] = await Promise.all([
      this.projects.toArray(),
      this.activityLogs.toArray(),
      this.preferences.toArray(),
      this.sessions.toArray()
    ]);

    return {
      version: 1,
      exportDate: new Date().toISOString(),
      data: {
        projects,
        activityLogs,
        preferences,
        sessions
      }
    };
  }

  // Import data from backup
  async importData(backupData: any) {
    if (backupData.version !== 1) {
      throw new Error('Unsupported backup version');
    }

    await this.transaction('rw', this.projects, this.activityLogs, this.preferences, this.sessions, async () => {
      if (backupData.data.projects) {
        await this.projects.bulkPut(backupData.data.projects);
      }
      if (backupData.data.activityLogs) {
        await this.activityLogs.bulkPut(backupData.data.activityLogs);
      }
      if (backupData.data.preferences) {
        await this.preferences.bulkPut(backupData.data.preferences);
      }
      if (backupData.data.sessions) {
        await this.sessions.bulkPut(backupData.data.sessions);
      }
    });
  }

  // Clear all data
  async clearAllData() {
    await this.transaction('rw', this.projects, this.activityLogs, this.preferences, this.sessions, async () => {
      await this.projects.clear();
      await this.activityLogs.clear();
      await this.preferences.clear();
      await this.sessions.clear();
    });
  }
}

// Export singleton instance
export const db = new LasomoiDB();
