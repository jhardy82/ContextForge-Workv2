/**
 * Shared Configuration Bridge for VS Code Extension
 *
 * This module provides a bridge to the shared configuration system
 * without TypeScript compilation issues related to file paths.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

export interface SharedTaskManConfig {
  version: string;
  lastUpdated: string;
  updatedBy: 'system' | 'ui' | 'extension' | 'user';

  database: {
    type: 'local' | 'sqlite' | 'dtm-api' | 'postgres';
    postgres?: {
      host: string;
      port: number;
      database: string;
      user: string;
      password: string;
      ssl: boolean;
      poolSize: number;
      connectionTimeout: number;
      idleTimeout: number;
      maxRetries: number;
    };
    sqlite?: {
      path: string;
      timeout: number;
      pragmas: {
        foreign_keys: boolean;
        journal_mode: string;
        synchronous: string;
      };
    };
    dtmApi?: {
      baseUrl: string;
      timeout: number;
      retryAttempts: number;
      healthCheck: string;
    };
    autoRefresh: boolean;
    refreshInterval: number;
  };

  dtm: {
    enableIntegration: boolean;
    serverPort: number;
    autoStart: boolean;
    frontendPort: number;
    healthCheckInterval: number;
    maxRetries: number;
  };

  ui: {
    theme: 'light' | 'dark' | 'system';
    compactView: boolean;
    showTaskDetails: boolean;
    showDueDates: boolean;
    showPriority: boolean;
    dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
    timeFormat: '12h' | '24h';
    startOfWeek: 'sunday' | 'monday';
  };

  notifications: {
    enabled: boolean;
    dueDates: boolean;
    statusChanges: boolean;
    overdueNotifications: boolean;
    digestFrequency: 'none' | 'daily' | 'weekly' | 'monthly';
  };

  sync: {
    enableAutoSync: boolean;
    conflictResolution: 'prompt' | 'local-wins' | 'remote-wins' | 'merge';
    syncInterval: number;
  };

  workspace: {
    trackWorkspaceChanges: boolean;
    excludePatterns: string[];
  };

  features: {
    enableSubtasks: boolean;
    maxSubtaskDepth: number;
    enableTeamFeatures: boolean;
    workflowAutomation: boolean;
    customStatuses: boolean;
  };

  storage: {
    mode: 'global' | 'workspace';
    backup: {
      enabled: boolean;
      frequency: 'hourly' | 'daily' | 'weekly';
      maxBackups: number;
    };
  };

  defaultGroups: string[];
  groupOrdering: string[];
}

export type SharedConfigChangeListener = (config: SharedTaskManConfig, changedKeys: string[]) => void;

export class SharedConfigBridge {
  private configPath: string;
  private config: SharedTaskManConfig | null = null;
  private fileWatcher: fs.FSWatcher | null = null;
  private listeners: Map<string, SharedConfigChangeListener> = new Map();
  private lastModified: number = 0;

  constructor() {
    // Get workspace folder
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
      throw new Error('No workspace folder found for shared configuration');
    }

    // Construct path to shared config file
    this.configPath = path.join(
      workspaceFolder.uri.fsPath,
      'TaskMan-v2',
      'shared',
      'config',
      'taskman-config.json'
    );

    this.loadConfig();
    this.setupFileWatcher();
  }

  /**
   * Get the current shared configuration
   */
  public getConfig(): SharedTaskManConfig {
    if (!this.config) {
      this.loadConfig();
    }
    return this.config!;
  }

  /**
   * Get a specific configuration value using dot notation
   */
  public get<T = any>(key: string, defaultValue?: T): T {
    const config = this.getConfig();
    const keys = key.split('.');
    let value: any = config;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue as T;
      }
    }

    return value as T;
  }

  /**
   * Set a specific configuration value using dot notation
   */
  public async set(key: string, value: any): Promise<void> {
    const config = { ...this.getConfig() };
    const keys = key.split('.');
    let current: any = config;

    // Navigate to the parent object
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in current) || typeof current[k] !== 'object') {
        current[k] = {};
      }
      current = current[k];
    }

    // Set the final value
    const finalKey = keys[keys.length - 1];
    current[finalKey] = value;

    // Update metadata
    config.lastUpdated = new Date().toISOString();
    config.updatedBy = 'extension';

    await this.saveConfig(config, [key]);
  }

  /**
   * Update multiple configuration values at once
   */
  public async updateConfig(updates: Partial<SharedTaskManConfig>): Promise<void> {
    const config = { ...this.getConfig(), ...updates };
    config.lastUpdated = new Date().toISOString();
    config.updatedBy = 'extension';

    const changedKeys = this.getChangedKeys(this.config!, updates);
    await this.saveConfig(config, changedKeys);
  }

  /**
   * Listen for configuration changes
   */
  public onConfigChange(id: string, listener: SharedConfigChangeListener): void {
    this.listeners.set(id, listener);
  }

  /**
   * Remove configuration change listener
   */
  public removeConfigListener(id: string): void {
    this.listeners.delete(id);
  }

  /**
   * Get configuration file path
   */
  public getConfigPath(): string {
    return this.configPath;
  }

  /**
   * Check if shared config file exists
   */
  public exists(): boolean {
    return fs.existsSync(this.configPath);
  }

  /**
   * Dispose resources
   */
  public dispose(): void {
    if (this.fileWatcher) {
      this.fileWatcher.close();
      this.fileWatcher = null;
    }
    this.listeners.clear();
  }

  // Private methods

  private loadConfig(): void {
    try {
      if (fs.existsSync(this.configPath)) {
        const configJson = fs.readFileSync(this.configPath, 'utf8');
        this.config = JSON.parse(configJson);

        // Update last modified time
        const stats = fs.statSync(this.configPath);
        this.lastModified = stats.mtime.getTime();
      } else {
        // Create default configuration if file doesn't exist
        this.config = this.getDefaultConfig();
        this.saveConfigSync(this.config);
      }
    } catch (error) {
      console.error('Failed to load shared TaskMan configuration:', error);
      this.config = this.getDefaultConfig();
    }
  }

  private async saveConfig(config: SharedTaskManConfig, changedKeys: string[]): Promise<void> {
    try {
      // Ensure directory exists
      const configDir = path.dirname(this.configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }

      // Write configuration file
      const configJson = JSON.stringify(config, null, 2);
      fs.writeFileSync(this.configPath, configJson, 'utf8');

      // Update internal state
      this.config = config;

      // Update last modified time
      const stats = fs.statSync(this.configPath);
      this.lastModified = stats.mtime.getTime();

      // Notify listeners
      this.notifyListeners(config, changedKeys);

    } catch (error) {
      console.error('Failed to save shared TaskMan configuration:', error);
      throw error;
    }
  }

  private saveConfigSync(config: SharedTaskManConfig): void {
    try {
      const configDir = path.dirname(this.configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }

      const configJson = JSON.stringify(config, null, 2);
      fs.writeFileSync(this.configPath, configJson, 'utf8');
    } catch (error) {
      console.error('Failed to save shared TaskMan configuration synchronously:', error);
    }
  }

  private setupFileWatcher(): void {
    try {
      if (fs.existsSync(this.configPath)) {
        this.fileWatcher = fs.watch(this.configPath, (eventType) => {
          if (eventType === 'change') {
            // Debounce file changes
            setTimeout(() => {
              try {
                const stats = fs.statSync(this.configPath);
                if (stats.mtime.getTime() > this.lastModified) {
                  this.loadConfig();
                  this.notifyListeners(this.config!, ['*']);
                }
              } catch (error) {
                console.error('Error handling config file change:', error);
              }
            }, 100);
          }
        });
      }
    } catch (error) {
      console.warn('Failed to setup shared configuration file watcher:', error);
    }
  }

  private notifyListeners(config: SharedTaskManConfig, changedKeys: string[]): void {
    this.listeners.forEach((listener) => {
      try {
        listener(config, changedKeys);
      } catch (error) {
        console.error('Shared configuration change listener error:', error);
      }
    });
  }

  private getChangedKeys(oldConfig: SharedTaskManConfig, updates: Partial<SharedTaskManConfig>): string[] {
    const changedKeys: string[] = [];

    const checkChanges = (obj1: any, obj2: any, prefix = '') => {
      for (const key in obj2) {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        if (typeof obj2[key] === 'object' && obj2[key] !== null && !Array.isArray(obj2[key])) {
          if (typeof obj1[key] === 'object' && obj1[key] !== null) {
            checkChanges(obj1[key], obj2[key], fullKey);
          } else {
            changedKeys.push(fullKey);
          }
        } else if (obj1[key] !== obj2[key]) {
          changedKeys.push(fullKey);
        }
      }
    };

    checkChanges(oldConfig, updates);
    return changedKeys;
  }

  private getDefaultConfig(): SharedTaskManConfig {
    return {
      version: '1.0.0',
      lastUpdated: new Date().toISOString(),
      updatedBy: 'system',

      database: {
        type: 'sqlite',
        sqlite: {
          path: '../../db/trackers.sqlite',
          timeout: 10000,
          pragmas: {
            foreign_keys: true,
            journal_mode: 'WAL',
            synchronous: 'NORMAL'
          }
        },
        dtmApi: {
          baseUrl: 'http://localhost:3001/api/v1',
          timeout: 5000,
          retryAttempts: 3,
          healthCheck: '/health'
        },
        autoRefresh: true,
        refreshInterval: 30
      },

      dtm: {
        enableIntegration: true,
        serverPort: 3001,
        autoStart: true,
        frontendPort: 5173,
        healthCheckInterval: 10,
        maxRetries: 5
      },

      ui: {
        theme: 'system',
        compactView: false,
        showTaskDetails: true,
        showDueDates: true,
        showPriority: true,
        dateFormat: 'MM/DD/YYYY',
        timeFormat: '12h',
        startOfWeek: 'monday'
      },

      notifications: {
        enabled: true,
        dueDates: true,
        statusChanges: true,
        overdueNotifications: true,
        digestFrequency: 'daily'
      },

      sync: {
        enableAutoSync: true,
        conflictResolution: 'prompt',
        syncInterval: 60
      },

      workspace: {
        trackWorkspaceChanges: true,
        excludePatterns: [
          'node_modules/**',
          '.git/**',
          '*.log',
          'tmp/**'
        ]
      },

      features: {
        enableSubtasks: true,
        maxSubtaskDepth: 3,
        enableTeamFeatures: false,
        workflowAutomation: false,
        customStatuses: false
      },

      storage: {
        mode: 'workspace',
        backup: {
          enabled: true,
          frequency: 'daily',
          maxBackups: 7
        }
      },

      defaultGroups: [
        'Today',
        'Upcoming',
        'Completed'
      ],

      groupOrdering: [
        'Today',
        'Upcoming',
        'In Progress',
        'Completed'
      ]
    };
  }
}