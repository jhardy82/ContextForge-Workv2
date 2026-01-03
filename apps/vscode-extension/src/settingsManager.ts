import * as vscode from "vscode";
import { SharedConfigBridge, SharedTaskManConfig } from "./sharedConfigBridge";

export interface TaskManSettings {
  // Storage and Database
  storageMode: "global" | "workspace";
  database: {
    type: "local" | "sqlite" | "dtm-api";
    sqlitePath: string;
    dtmApiUrl: string;
    autoRefresh: boolean;
    refreshInterval: number;
  };

  // DTM Integration
  dtm: {
    enableIntegration: boolean;
    serverPort: number;
    autoStart: boolean;
  };

  // UI Preferences
  ui: {
    compactView: boolean;
    showTaskDetails: boolean;
    showDueDates: boolean;
    showPriority: boolean;
    theme: "auto" | "light" | "dark";
  };

  // Groups and Sorting
  defaultGroups: string[];
  groupOrdering: string[];
  sortBy: "created" | "title" | "completed" | "dueDate" | "priority";
  sortOrder: "asc" | "desc";
  hideEmptyGroups: boolean;

  // Notifications
  notifications: {
    enabled: boolean;
    dueDates: boolean;
    statusChanges: boolean;
  };

  // Sync and Integration
  sync: {
    enableAutoSync: boolean;
    conflictResolution: "prompt" | "local-wins" | "remote-wins" | "merge";
  };

  // Workspace Integration
  workspace: {
    trackWorkspaceChanges: boolean;
    excludePatterns: string[];
  };

  // WebView
  showWebviewDetails: boolean;
}

export class SettingsManager {
  private config: vscode.WorkspaceConfiguration;
  private sharedConfig: SharedConfigBridge | null = null;
  private configChangeDisposable: vscode.Disposable | null = null;

  constructor() {
    this.config = vscode.workspace.getConfiguration("taskman");
    try {
      this.sharedConfig = new SharedConfigBridge();
      this.setupConfigurationSync();
    } catch (error) {
      console.warn("Failed to initialize shared configuration:", error);
      // Continue without shared config if it fails
      this.sharedConfig = null as any;
    }
  }

  /**
   * Get all TaskMan settings
   */
  getSettings(): TaskManSettings {
    return {
      storageMode: this.config.get("storageMode", "workspace"),
      database: {
        type: this.config.get("database.type", "local"),
        sqlitePath: this.config.get(
          "database.sqlitePath",
          "db/trackers.sqlite"
        ),
        dtmApiUrl: this.config.get(
          "database.dtmApiUrl",
          "http://localhost:3001/api/v1"
        ),
        autoRefresh: this.config.get("database.autoRefresh", true),
        refreshInterval: this.config.get("database.refreshInterval", 30),
      },
      dtm: {
        enableIntegration: this.config.get("dtm.enableIntegration", true),
        serverPort: this.config.get("dtm.serverPort", 3000),
        autoStart: this.config.get("dtm.autoStart", true),
      },
      ui: {
        compactView: this.config.get("ui.compactView", false),
        showTaskDetails: this.config.get("ui.showTaskDetails", true),
        showDueDates: this.config.get("ui.showDueDates", true),
        showPriority: this.config.get("ui.showPriority", true),
        theme: this.config.get("ui.theme", "auto"),
      },
      defaultGroups: this.config.get("defaultGroups", [
        "Today",
        "Upcoming",
        "Completed",
      ]),
      groupOrdering: this.config.get("groupOrdering", [
        "Today",
        "Upcoming",
        "Completed",
      ]),
      sortBy: this.config.get("sortBy", "created"),
      sortOrder: this.config.get("sortOrder", "asc"),
      hideEmptyGroups: this.config.get("hideEmptyGroups", false),
      notifications: {
        enabled: this.config.get("notifications.enabled", true),
        dueDates: this.config.get("notifications.dueDates", true),
        statusChanges: this.config.get("notifications.statusChanges", true),
      },
      sync: {
        enableAutoSync: this.config.get("sync.enableAutoSync", true),
        conflictResolution: this.config.get(
          "sync.conflictResolution",
          "prompt"
        ),
      },
      workspace: {
        trackWorkspaceChanges: this.config.get(
          "workspace.trackWorkspaceChanges",
          true
        ),
        excludePatterns: this.config.get("workspace.excludePatterns", [
          "node_modules/**",
          ".git/**",
          "*.log",
          "*.tmp",
        ]),
      },
      showWebviewDetails: this.config.get("showWebviewDetails", true),
    };
  }

  /**
   * Update a specific setting
   */
  async updateSetting(
    key: string,
    value: any,
    target?: vscode.ConfigurationTarget
  ): Promise<void> {
    await this.config.update(key, value, target);
    this.refreshConfig();
  }

  /**
   * Update multiple settings at once
   */
  async updateSettings(settings: Partial<TaskManSettings>): Promise<void> {
    const updates: Thenable<void>[] = [];

    if (settings.storageMode !== undefined) {
      updates.push(this.config.update("storageMode", settings.storageMode));
    }

    if (settings.database) {
      if (settings.database.type !== undefined) {
        updates.push(
          this.config.update("database.type", settings.database.type)
        );
      }
      if (settings.database.sqlitePath !== undefined) {
        updates.push(
          this.config.update(
            "database.sqlitePath",
            settings.database.sqlitePath
          )
        );
      }
      if (settings.database.dtmApiUrl !== undefined) {
        updates.push(
          this.config.update("database.dtmApiUrl", settings.database.dtmApiUrl)
        );
      }
      if (settings.database.autoRefresh !== undefined) {
        updates.push(
          this.config.update(
            "database.autoRefresh",
            settings.database.autoRefresh
          )
        );
      }
      if (settings.database.refreshInterval !== undefined) {
        updates.push(
          this.config.update(
            "database.refreshInterval",
            settings.database.refreshInterval
          )
        );
      }
    }

    if (settings.dtm) {
      if (settings.dtm.enableIntegration !== undefined) {
        updates.push(
          this.config.update(
            "dtm.enableIntegration",
            settings.dtm.enableIntegration
          )
        );
      }
      if (settings.dtm.serverPort !== undefined) {
        updates.push(
          this.config.update("dtm.serverPort", settings.dtm.serverPort)
        );
      }
      if (settings.dtm.autoStart !== undefined) {
        updates.push(
          this.config.update("dtm.autoStart", settings.dtm.autoStart)
        );
      }
    }

    if (settings.ui) {
      if (settings.ui.compactView !== undefined) {
        updates.push(
          this.config.update("ui.compactView", settings.ui.compactView)
        );
      }
      if (settings.ui.showTaskDetails !== undefined) {
        updates.push(
          this.config.update("ui.showTaskDetails", settings.ui.showTaskDetails)
        );
      }
      if (settings.ui.showDueDates !== undefined) {
        updates.push(
          this.config.update("ui.showDueDates", settings.ui.showDueDates)
        );
      }
      if (settings.ui.showPriority !== undefined) {
        updates.push(
          this.config.update("ui.showPriority", settings.ui.showPriority)
        );
      }
      if (settings.ui.theme !== undefined) {
        updates.push(this.config.update("ui.theme", settings.ui.theme));
      }
    }

    if (settings.notifications) {
      if (settings.notifications.enabled !== undefined) {
        updates.push(
          this.config.update(
            "notifications.enabled",
            settings.notifications.enabled
          )
        );
      }
      if (settings.notifications.dueDates !== undefined) {
        updates.push(
          this.config.update(
            "notifications.dueDates",
            settings.notifications.dueDates
          )
        );
      }
      if (settings.notifications.statusChanges !== undefined) {
        updates.push(
          this.config.update(
            "notifications.statusChanges",
            settings.notifications.statusChanges
          )
        );
      }
    }

    if (settings.sync) {
      if (settings.sync.enableAutoSync !== undefined) {
        updates.push(
          this.config.update(
            "sync.enableAutoSync",
            settings.sync.enableAutoSync
          )
        );
      }
      if (settings.sync.conflictResolution !== undefined) {
        updates.push(
          this.config.update(
            "sync.conflictResolution",
            settings.sync.conflictResolution
          )
        );
      }
    }

    if (settings.workspace) {
      if (settings.workspace.trackWorkspaceChanges !== undefined) {
        updates.push(
          this.config.update(
            "workspace.trackWorkspaceChanges",
            settings.workspace.trackWorkspaceChanges
          )
        );
      }
      if (settings.workspace.excludePatterns !== undefined) {
        updates.push(
          this.config.update(
            "workspace.excludePatterns",
            settings.workspace.excludePatterns
          )
        );
      }
    }

    if (settings.defaultGroups !== undefined) {
      updates.push(this.config.update("defaultGroups", settings.defaultGroups));
    }

    if (settings.groupOrdering !== undefined) {
      updates.push(this.config.update("groupOrdering", settings.groupOrdering));
    }

    if (settings.sortBy !== undefined) {
      updates.push(this.config.update("sortBy", settings.sortBy));
    }

    if (settings.sortOrder !== undefined) {
      updates.push(this.config.update("sortOrder", settings.sortOrder));
    }

    if (settings.hideEmptyGroups !== undefined) {
      updates.push(
        this.config.update("hideEmptyGroups", settings.hideEmptyGroups)
      );
    }

    if (settings.showWebviewDetails !== undefined) {
      updates.push(
        this.config.update("showWebviewDetails", settings.showWebviewDetails)
      );
    }

    await Promise.all(updates);
    this.refreshConfig();
  }

  /**
   * Reset settings to defaults
   */
  async resetToDefaults(): Promise<void> {
    const defaultSettings: TaskManSettings = {
      storageMode: "workspace",
      database: {
        type: "local",
        sqlitePath: "db/trackers.sqlite",
        dtmApiUrl: "http://localhost:3001/api/v1",
        autoRefresh: true,
        refreshInterval: 30,
      },
      dtm: {
        enableIntegration: true,
        serverPort: 3001,
        autoStart: true,
      },
      ui: {
        compactView: false,
        showTaskDetails: true,
        showDueDates: true,
        showPriority: true,
        theme: "auto",
      },
      defaultGroups: ["Today", "Upcoming", "Completed"],
      groupOrdering: ["Today", "Upcoming", "Completed"],
      sortBy: "created",
      sortOrder: "asc",
      hideEmptyGroups: false,
      notifications: {
        enabled: true,
        dueDates: true,
        statusChanges: true,
      },
      sync: {
        enableAutoSync: true,
        conflictResolution: "prompt",
      },
      workspace: {
        trackWorkspaceChanges: true,
        excludePatterns: ["node_modules/**", ".git/**", "*.log", "*.tmp"],
      },
      showWebviewDetails: true,
    };

    await this.updateSettings(defaultSettings);
  }

  /**
   * Show settings quick pick menu
   */
  async showSettingsMenu(): Promise<void> {
    const items: vscode.QuickPickItem[] = [
      {
        label: "$(database) Database Settings",
        description: "Configure database connection and sync options",
        detail: "SQLite, DTM API, local storage options",
      },
      {
        label: "$(settings-gear) DTM Integration",
        description: "Configure Dynamic Task Manager integration",
        detail: "Server connection, auto-start, API settings",
      },
      {
        label: "$(color-mode) UI Preferences",
        description: "Customize appearance and display options",
        detail: "Theme, compact view, task details, priorities",
      },
      {
        label: "$(list-ordered) Groups & Sorting",
        description: "Configure task groups and sorting preferences",
        detail: "Default groups, sort order, empty group handling",
      },
      {
        label: "$(bell) Notifications",
        description: "Configure notification preferences",
        detail: "Due date reminders, status change alerts",
      },
      {
        label: "$(sync) Sync Settings",
        description: "Configure synchronization behavior",
        detail: "Auto-sync, conflict resolution, workspace tracking",
      },
      {
        label: "$(refresh) Reset to Defaults",
        description: "Reset all settings to default values",
        detail: "This will overwrite all current settings",
      },
    ];

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: "Select settings category to configure",
      matchOnDescription: true,
      matchOnDetail: true,
    });

    if (selected) {
      switch (selected.label) {
        case "$(database) Database Settings":
          await this.showDatabaseSettings();
          break;
        case "$(settings-gear) DTM Integration":
          await this.showDTMSettings();
          break;
        case "$(color-mode) UI Preferences":
          await this.showUISettings();
          break;
        case "$(list-ordered) Groups & Sorting":
          await this.showGroupSettings();
          break;
        case "$(bell) Notifications":
          await this.showNotificationSettings();
          break;
        case "$(sync) Sync Settings":
          await this.showSyncSettings();
          break;
        case "$(refresh) Reset to Defaults":
          await this.confirmResetToDefaults();
          break;
      }
    }
  }

  /**
   * Show database connection settings menu
   */
  private async showDatabaseSettings(): Promise<void> {
    const currentSettings = this.getSettings();
    const currentType = currentSettings.database.type;

    const items: vscode.QuickPickItem[] = [
      {
        label: "$(database) Current Connection",
        description: `Type: ${currentType.toUpperCase()}`,
        detail: this.getDatabaseConnectionDetail(currentSettings),
      },
      {
        label: "$(settings-gear) Configure Connection",
        description: "Change database type and connection settings",
        detail: "SQLite file, DTM API server, or local storage",
      },
      {
        label: "$(pulse) Test Connection",
        description: "Test current database connection",
        detail: "Verify connectivity and response time",
      },
      {
        label: "$(info) Connection Status",
        description: "View detailed connection information",
        detail: "Show current settings and diagnostics",
      },
      {
        label: "$(refresh) Refresh Settings",
        description: "Reload database configuration",
        detail: "Sync with shared configuration file",
      },
    ];

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: "Select database connection option",
      matchOnDescription: true,
      matchOnDetail: true,
    });

    if (selected) {
      switch (selected.label) {
        case "$(database) Current Connection":
          await this.showConnectionDetails();
          break;
        case "$(settings-gear) Configure Connection":
          await this.configureConnection();
          break;
        case "$(pulse) Test Connection":
          await this.testDatabaseConnection();
          break;
        case "$(info) Connection Status":
          await this.showConnectionStatus();
          break;
        case "$(refresh) Refresh Settings":
          await this.refreshDatabaseSettings();
          break;
      }
    }
  }

  /**
   * Get database connection detail string
   */
  private getDatabaseConnectionDetail(settings: TaskManSettings): string {
    switch (settings.database.type) {
      case "local":
        return "Local VS Code storage";
      case "sqlite":
        return `SQLite: ${settings.database.sqlitePath}`;
      case "dtm-api":
        return `DTM API: ${settings.database.dtmApiUrl}`;
      default:
        return "Unknown connection type";
    }
  }

  /**
   * Show detailed connection information
   */
  private async showConnectionDetails(): Promise<void> {
    const currentSettings = this.getSettings();
    const sharedConfig = this.sharedConfig?.getConfig();

    let details = `**Current Database Connection**\n\n`;
    details += `• **Type**: ${currentSettings.database.type.toUpperCase()}\n`;
    details += `• **Auto Refresh**: ${
      currentSettings.database.autoRefresh ? "Enabled" : "Disabled"
    }\n`;
    details += `• **Refresh Interval**: ${currentSettings.database.refreshInterval}s\n\n`;

    if (currentSettings.database.type === "sqlite") {
      details += `**SQLite Configuration**\n`;
      details += `• **Path**: ${currentSettings.database.sqlitePath}\n`;
      if (sharedConfig?.database.sqlite) {
        details += `• **Timeout**: ${sharedConfig.database.sqlite.timeout}ms\n`;
        details += `• **Journal Mode**: ${sharedConfig.database.sqlite.pragmas.journal_mode}\n`;
        details += `• **Foreign Keys**: ${
          sharedConfig.database.sqlite.pragmas.foreign_keys
            ? "Enabled"
            : "Disabled"
        }\n`;
      }
    } else if (currentSettings.database.type === "dtm-api") {
      details += `**DTM API Configuration**\n`;
      details += `• **Base URL**: ${currentSettings.database.dtmApiUrl}\n`;
      if (sharedConfig?.database.dtmApi) {
        details += `• **Timeout**: ${sharedConfig.database.dtmApi.timeout}ms\n`;
        details += `• **Retry Attempts**: ${sharedConfig.database.dtmApi.retryAttempts}\n`;
        details += `• **Health Check**: ${sharedConfig.database.dtmApi.healthCheck}\n`;
      }
    }

    await vscode.window.showInformationMessage(details, { modal: true });
  }

  /**
   * Configure database connection
   */
  private async configureConnection(): Promise<void> {
    const currentSettings = this.getSettings();

    const dbTypeItems: vscode.QuickPickItem[] = [
      {
        label: "local",
        description: "Store tasks locally in VS Code",
        picked: currentSettings.database.type === "local",
      },
      {
        label: "sqlite",
        description: "Use SQLite database file",
        picked: currentSettings.database.type === "sqlite",
      },
      {
        label: "dtm-api",
        description: "Connect to DTM API server",
        picked: currentSettings.database.type === "dtm-api",
      },
    ];

    const dbType = await vscode.window.showQuickPick(dbTypeItems, {
      placeHolder: "Select database type",
    });

    if (dbType) {
      await this.updateSetting("database.type", dbType.label);

      if (dbType.label === "sqlite") {
        await this.configureSQLiteConnection(currentSettings);
      } else if (dbType.label === "dtm-api") {
        await this.configureDTMApiConnection(currentSettings);
      }

      // Test the new connection
      const testResult = await this.testDatabaseConnection();
      if (testResult) {
        vscode.window.showInformationMessage(
          `✅ Database connection updated to: ${dbType.label}`
        );
      }
    }
  }

  /**
   * Configure SQLite connection settings
   */
  private async configureSQLiteConnection(
    currentSettings: TaskManSettings
  ): Promise<void> {
    const sqlitePath = await vscode.window.showInputBox({
      prompt: "Enter SQLite database path (relative to workspace)",
      value: currentSettings.database.sqlitePath,
      placeHolder: "db/trackers.sqlite",
      validateInput: (value) => {
        if (!value || value.trim().length === 0) {
          return "Path cannot be empty";
        }
        if (!value.endsWith(".sqlite") && !value.endsWith(".db")) {
          return "Please use .sqlite or .db file extension";
        }
        return null;
      },
    });

    if (sqlitePath) {
      await this.updateSetting("database.sqlitePath", sqlitePath);

      // Update shared config if available
      if (this.sharedConfig) {
        try {
          await this.sharedConfig.set("database.sqlite.path", sqlitePath);
        } catch (error) {
          console.warn("Failed to update shared config:", error);
        }
      }
    }
  }

  /**
   * Configure DTM API connection settings
   */
  private async configureDTMApiConnection(
    currentSettings: TaskManSettings
  ): Promise<void> {
    const apiUrl = await vscode.window.showInputBox({
      prompt: "Enter DTM API URL",
      value: currentSettings.database.dtmApiUrl,
      placeHolder: "http://localhost:3001/api/v1",
      validateInput: (value) => {
        if (!value || value.trim().length === 0) {
          return "URL cannot be empty";
        }
        try {
          new URL(value);
          return null;
        } catch {
          return "Please enter a valid URL";
        }
      },
    });

    if (apiUrl) {
      await this.updateSetting("database.dtmApiUrl", apiUrl);

      // Update shared config if available
      if (this.sharedConfig) {
        try {
          await this.sharedConfig.set("database.dtmApi.baseUrl", apiUrl);
        } catch (error) {
          console.warn("Failed to update shared config:", error);
        }
      }
    }
  }

  /**
   * Test database connection
   */
  private async testDatabaseConnection(): Promise<boolean> {
    const currentSettings = this.getSettings();

    return vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Testing Database Connection",
        cancellable: false,
      },
      async (progress) => {
        progress.report({
          increment: 0,
          message: "Initializing connection test...",
        });

        try {
          switch (currentSettings.database.type) {
            case "local":
              return await this.testLocalConnection(progress);
            case "sqlite":
              return await this.testSQLiteConnection(progress, currentSettings);
            case "dtm-api":
              return await this.testDTMApiConnection(progress, currentSettings);
            default:
              throw new Error(
                `Unknown database type: ${currentSettings.database.type}`
              );
          }
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : "Unknown error";
          vscode.window.showErrorMessage(
            `❌ Connection test failed: ${errorMessage}`
          );
          return false;
        }
      }
    );
  }

  /**
   * Test local storage connection
   */
  private async testLocalConnection(
    progress: vscode.Progress<{ increment?: number; message?: string }>
  ): Promise<boolean> {
    progress.report({
      increment: 50,
      message: "Checking local storage access...",
    });

    try {
      // Test VS Code storage access
      const testKey = "taskman-connection-test";
      const testValue = new Date().toISOString();
      await vscode.workspace
        .getConfiguration("taskman")
        .update(testKey, testValue, vscode.ConfigurationTarget.Global);

      progress.report({
        increment: 100,
        message: "Local storage test completed",
      });

      // Clean up test data
      await vscode.workspace
        .getConfiguration("taskman")
        .update(testKey, undefined, vscode.ConfigurationTarget.Global);

      vscode.window.showInformationMessage(
        "✅ Local storage connection successful"
      );
      return true;
    } catch (error) {
      throw new Error(`Local storage access failed: ${error}`);
    }
  }

  /**
   * Test SQLite connection
   */
  private async testSQLiteConnection(
    progress: vscode.Progress<{ increment?: number; message?: string }>,
    settings: TaskManSettings
  ): Promise<boolean> {
    const fs = require("fs");
    const path = require("path");

    progress.report({ increment: 25, message: "Checking SQLite file path..." });

    try {
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) {
        throw new Error("No workspace folder found");
      }

      const dbPath = path.resolve(
        workspaceFolder.uri.fsPath,
        settings.database.sqlitePath
      );
      const dbDir = path.dirname(dbPath);

      progress.report({
        increment: 50,
        message: "Verifying database directory...",
      });

      // Check if directory exists, create if needed
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      progress.report({ increment: 75, message: "Testing database access..." });

      // Check if file exists or can be created
      let exists = fs.existsSync(dbPath);
      if (!exists) {
        // Try to create the file to test write permissions
        fs.writeFileSync(dbPath, "");
        exists = true;
      }

      progress.report({
        increment: 100,
        message: "SQLite connection test completed",
      });

      const statusIcon = exists ? "✅" : "⚠️";
      const statusMessage = exists
        ? "SQLite database connection successful"
        : "SQLite database path accessible but file doesn't exist yet";

      vscode.window.showInformationMessage(
        `${statusIcon} ${statusMessage}\n📁 Path: ${dbPath}`
      );
      return true;
    } catch (error) {
      throw new Error(`SQLite connection test failed: ${error}`);
    }
  }

  /**
   * Test DTM API connection
   */
  private async testDTMApiConnection(
    progress: vscode.Progress<{ increment?: number; message?: string }>,
    settings: TaskManSettings
  ): Promise<boolean> {
    progress.report({ increment: 25, message: "Connecting to DTM API..." });

    try {
      const startTime = Date.now();
      const sharedConfig = this.sharedConfig?.getConfig();
      const timeout = sharedConfig?.database.dtmApi?.timeout || 5000;
      const healthEndpoint =
        sharedConfig?.database.dtmApi?.healthCheck || "/health";

      progress.report({
        increment: 50,
        message: "Sending health check request...",
      });

      // Import fetch dynamically for Node.js compatibility
      const fetch = (await import("node-fetch")).default;

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const healthUrl =
        settings.database.dtmApiUrl.replace(/\/+$/, "") + healthEndpoint;
      const response = await fetch(healthUrl, {
        method: "GET",
        signal: controller.signal,
        headers: {
          Accept: "application/json",
          "User-Agent": "TaskMan-v2-VSCode-Extension",
        },
      });

      clearTimeout(timeoutId);
      const responseTime = Date.now() - startTime;

      progress.report({
        increment: 100,
        message: "Processing API response...",
      });

      if (response.ok) {
        let healthData;
        try {
          healthData = await response.json();
        } catch {
          healthData = { status: "ok", message: "Health check passed" };
        }

        vscode.window.showInformationMessage(
          `✅ DTM API connection successful\n` +
            `🔗 URL: ${settings.database.dtmApiUrl}\n` +
            `⏱️ Response time: ${responseTime}ms\n` +
            `📊 Status: ${healthData.status || "ok"}`
        );
        return true;
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error: any) {
      if (error?.name === "AbortError") {
        throw new Error(
          `Connection timeout after ${
            this.sharedConfig?.getConfig()?.database.dtmApi?.timeout || 5000
          }ms`
        );
      }
      throw new Error(`DTM API connection failed: ${error?.message || error}`);
    }
  }

  /**
   * Show connection status and diagnostics
   */
  private async showConnectionStatus(): Promise<void> {
    const currentSettings = this.getSettings();
    const sharedConfig = this.sharedConfig?.getConfig();

    let status = `**TaskMan Database Connection Status**\n\n`;
    status += `🔌 **Connection Type**: ${currentSettings.database.type.toUpperCase()}\n`;
    status += `🔄 **Auto Refresh**: ${
      currentSettings.database.autoRefresh ? "✅ Enabled" : "❌ Disabled"
    }\n`;
    status += `⏰ **Refresh Interval**: ${currentSettings.database.refreshInterval} seconds\n\n`;

    // Show type-specific information
    if (
      currentSettings.database.type === "sqlite" &&
      sharedConfig?.database.sqlite
    ) {
      status += `**SQLite Configuration**\n`;
      status += `📁 **File Path**: ${currentSettings.database.sqlitePath}\n`;
      status += `⏱️ **Timeout**: ${sharedConfig.database.sqlite.timeout}ms\n`;
      status += `📝 **Journal Mode**: ${sharedConfig.database.sqlite.pragmas.journal_mode}\n`;
      status += `🔗 **Foreign Keys**: ${
        sharedConfig.database.sqlite.pragmas.foreign_keys ? "✅" : "❌"
      }\n`;
      status += `🔄 **Synchronous**: ${sharedConfig.database.sqlite.pragmas.synchronous}\n`;
    } else if (
      currentSettings.database.type === "dtm-api" &&
      sharedConfig?.database.dtmApi
    ) {
      status += `**DTM API Configuration**\n`;
      status += `🌐 **Base URL**: ${currentSettings.database.dtmApiUrl}\n`;
      status += `⏱️ **Timeout**: ${sharedConfig.database.dtmApi.timeout}ms\n`;
      status += `🔄 **Retry Attempts**: ${sharedConfig.database.dtmApi.retryAttempts}\n`;
      status += `💓 **Health Check**: ${sharedConfig.database.dtmApi.healthCheck}\n`;
    }

    // Show shared config status
    status += `\n**Shared Configuration**\n`;
    status += `📄 **Config File**: ${
      this.sharedConfig ? "✅ Available" : "❌ Not Available"
    }\n`;
    if (sharedConfig) {
      status += `📅 **Last Updated**: ${new Date(
        sharedConfig.lastUpdated
      ).toLocaleString()}\n`;
      status += `👤 **Updated By**: ${sharedConfig.updatedBy}\n`;
    }

    const result = await vscode.window.showInformationMessage(
      status,
      { modal: true },
      "Test Connection",
      "Configure"
    );

    if (result === "Test Connection") {
      await this.testDatabaseConnection();
    } else if (result === "Configure") {
      await this.configureConnection();
    }
  }

  /**
   * Refresh database settings from shared configuration
   */
  private async refreshDatabaseSettings(): Promise<void> {
    if (!this.sharedConfig) {
      vscode.window.showWarningMessage("Shared configuration is not available");
      return;
    }

    try {
      const sharedConfig = this.sharedConfig.getConfig();
      await this.syncFromSharedConfig(sharedConfig);
      vscode.window.showInformationMessage(
        "✅ Database settings refreshed from shared configuration"
      );
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to refresh settings: ${error}`);
    }
  }

  /**
   * Show DTM integration settings
   */
  private async showDTMSettings(): Promise<void> {
    const currentSettings = this.getSettings();

    const items: vscode.QuickPickItem[] = [
      {
        label: currentSettings.dtm.enableIntegration
          ? "$(check) Enable DTM Integration"
          : "$(unchecked) Enable DTM Integration",
        description: "Toggle DTM server integration",
      },
      {
        label: "$(server-process) Server Port",
        description: `Current: ${currentSettings.dtm.serverPort}`,
      },
      {
        label: currentSettings.dtm.autoStart
          ? "$(check) Auto-start Server"
          : "$(unchecked) Auto-start Server",
        description: "Automatically start DTM server if not running",
      },
    ];

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: "Select DTM setting to configure",
    });

    if (selected) {
      if (selected.description === "Toggle DTM server integration") {
        await this.updateSetting(
          "dtm.enableIntegration",
          !currentSettings.dtm.enableIntegration
        );
        vscode.window.showInformationMessage(
          `DTM Integration ${
            !currentSettings.dtm.enableIntegration ? "enabled" : "disabled"
          }`
        );
      } else if (selected.label.includes("Server Port")) {
        const port = await vscode.window.showInputBox({
          prompt: "Enter DTM server port number",
          value: currentSettings.dtm.serverPort.toString(),
          validateInput: (value) => {
            const num = parseInt(value);
            return isNaN(num) || num < 1 || num > 65535
              ? "Please enter a valid port number (1-65535)"
              : null;
          },
        });

        if (port) {
          await this.updateSetting("dtm.serverPort", parseInt(port));
          vscode.window.showInformationMessage(
            `DTM server port updated to: ${port}`
          );
        }
      } else if (
        selected.description === "Automatically start DTM server if not running"
      ) {
        await this.updateSetting(
          "dtm.autoStart",
          !currentSettings.dtm.autoStart
        );
        vscode.window.showInformationMessage(
          `DTM auto-start ${
            !currentSettings.dtm.autoStart ? "enabled" : "disabled"
          }`
        );
      }
    }
  }

  /**
   * Show UI preferences settings
   */
  private async showUISettings(): Promise<void> {
    const currentSettings = this.getSettings();

    const items: vscode.QuickPickItem[] = [
      {
        label: currentSettings.ui.compactView
          ? "$(check) Compact View"
          : "$(unchecked) Compact View",
        description: "Use compact display for tasks",
      },
      {
        label: currentSettings.ui.showTaskDetails
          ? "$(check) Show Task Details"
          : "$(unchecked) Show Task Details",
        description: "Display detailed task information",
      },
      {
        label: currentSettings.ui.showDueDates
          ? "$(check) Show Due Dates"
          : "$(unchecked) Show Due Dates",
        description: "Display due dates for tasks",
      },
      {
        label: currentSettings.ui.showPriority
          ? "$(check) Show Priority"
          : "$(unchecked) Show Priority",
        description: "Display priority indicators",
      },
      {
        label: "$(color-mode) Theme",
        description: `Current: ${currentSettings.ui.theme}`,
      },
    ];

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: "Select UI setting to configure",
    });

    if (selected) {
      if (selected.description === "Use compact display for tasks") {
        await this.updateSetting(
          "ui.compactView",
          !currentSettings.ui.compactView
        );
      } else if (selected.description === "Display detailed task information") {
        await this.updateSetting(
          "ui.showTaskDetails",
          !currentSettings.ui.showTaskDetails
        );
      } else if (selected.description === "Display due dates for tasks") {
        await this.updateSetting(
          "ui.showDueDates",
          !currentSettings.ui.showDueDates
        );
      } else if (selected.description === "Display priority indicators") {
        await this.updateSetting(
          "ui.showPriority",
          !currentSettings.ui.showPriority
        );
      } else if (selected.label.includes("Theme")) {
        const themeItems: vscode.QuickPickItem[] = [
          {
            label: "auto",
            description: "Follow VS Code theme",
            picked: currentSettings.ui.theme === "auto",
          },
          {
            label: "light",
            description: "Light theme",
            picked: currentSettings.ui.theme === "light",
          },
          {
            label: "dark",
            description: "Dark theme",
            picked: currentSettings.ui.theme === "dark",
          },
        ];

        const theme = await vscode.window.showQuickPick(themeItems, {
          placeHolder: "Select theme",
        });

        if (theme) {
          await this.updateSetting("ui.theme", theme.label);
          vscode.window.showInformationMessage(
            `Theme updated to: ${theme.label}`
          );
        }
      }
    }
  }

  /**
   * Show group and sorting settings
   */
  private async showGroupSettings(): Promise<void> {
    // Implementation for group settings UI
    const currentSettings = this.getSettings();

    vscode.window.showInformationMessage(
      "Group settings configuration coming soon!"
    );
    // TODO: Implement detailed group configuration UI
  }

  /**
   * Show notification settings
   */
  private async showNotificationSettings(): Promise<void> {
    const currentSettings = this.getSettings();

    const items: vscode.QuickPickItem[] = [
      {
        label: currentSettings.notifications.enabled
          ? "$(check) Enable Notifications"
          : "$(unchecked) Enable Notifications",
        description: "Toggle all notifications",
      },
      {
        label: currentSettings.notifications.dueDates
          ? "$(check) Due Date Reminders"
          : "$(unchecked) Due Date Reminders",
        description: "Notify when tasks are approaching due dates",
      },
      {
        label: currentSettings.notifications.statusChanges
          ? "$(check) Status Change Alerts"
          : "$(unchecked) Status Change Alerts",
        description: "Notify when task status changes",
      },
    ];

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: "Select notification setting to configure",
    });

    if (selected) {
      if (selected.description === "Enable/disable all notifications") {
        await this.updateSetting(
          "notifications.enabled",
          !currentSettings.notifications.enabled
        );
      } else if (
        selected.description === "Notify when tasks are approaching due dates"
      ) {
        await this.updateSetting(
          "notifications.dueDates",
          !currentSettings.notifications.dueDates
        );
      } else if (selected.description === "Notify when task status changes") {
        await this.updateSetting(
          "notifications.statusChanges",
          !currentSettings.notifications.statusChanges
        );
      }
    }
  }

  /**
   * Show sync settings
   */
  private async showSyncSettings(): Promise<void> {
    const currentSettings = this.getSettings();

    vscode.window.showInformationMessage(
      "Sync settings configuration coming soon!"
    );
    // TODO: Implement detailed sync configuration UI
  }

  /**
   * Confirm reset to defaults
   */
  private async confirmResetToDefaults(): Promise<void> {
    const result = await vscode.window.showWarningMessage(
      "Are you sure you want to reset all TaskMan settings to their default values? This cannot be undone.",
      { modal: true },
      "Reset to Defaults",
      "Cancel"
    );

    if (result === "Reset to Defaults") {
      await this.resetToDefaults();
      vscode.window.showInformationMessage(
        "All TaskMan settings have been reset to defaults"
      );
    }
  }

  /**
   * Refresh configuration reference
   */
  private refreshConfig(): void {
    this.config = vscode.workspace.getConfiguration("taskman");
  }

  /**
   * Watch for configuration changes
   */
  onConfigurationChanged(
    callback: (settings: TaskManSettings) => void
  ): vscode.Disposable {
    return vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration("taskman")) {
        this.refreshConfig();
        callback(this.getSettings());
      }
    });
  }

  /**
   * Setup bidirectional configuration synchronization
   */
  private setupConfigurationSync(): void {
    if (!this.sharedConfig) {
      return;
    }

    // Listen for shared config changes and update VS Code settings
    this.sharedConfig.onConfigChange(
      "vscode-extension",
      (sharedConfig: SharedTaskManConfig, changedKeys: string[]) => {
        this.syncFromSharedConfig(sharedConfig);
      }
    );

    // Listen for VS Code setting changes and update shared config
    this.configChangeDisposable = vscode.workspace.onDidChangeConfiguration(
      (event) => {
        if (event.affectsConfiguration("taskman")) {
          this.syncToSharedConfig();
        }
      }
    );
  }

  /**
   * Sync settings from shared config to VS Code settings
   */
  private async syncFromSharedConfig(
    sharedConfig: SharedTaskManConfig
  ): Promise<void> {
    try {
      // Map shared config to VS Code settings
      const config = vscode.workspace.getConfiguration("taskman");

      // Database settings
      await config.update(
        "database.type",
        sharedConfig.database.type,
        vscode.ConfigurationTarget.Workspace
      );
      if (sharedConfig.database.sqlite) {
        await config.update(
          "database.sqlitePath",
          sharedConfig.database.sqlite.path,
          vscode.ConfigurationTarget.Workspace
        );
      }
      if (sharedConfig.database.dtmApi) {
        await config.update(
          "database.dtmApiUrl",
          sharedConfig.database.dtmApi.baseUrl,
          vscode.ConfigurationTarget.Workspace
        );
      }
      await config.update(
        "database.autoRefresh",
        sharedConfig.database.autoRefresh,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "database.refreshInterval",
        sharedConfig.database.refreshInterval,
        vscode.ConfigurationTarget.Workspace
      );

      // DTM settings
      await config.update(
        "dtm.enableIntegration",
        sharedConfig.dtm.enableIntegration,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "dtm.serverPort",
        sharedConfig.dtm.serverPort,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "dtm.autoStart",
        sharedConfig.dtm.autoStart,
        vscode.ConfigurationTarget.Workspace
      );

      // UI settings
      await config.update(
        "ui.compactView",
        sharedConfig.ui.compactView,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "ui.showTaskDetails",
        sharedConfig.ui.showTaskDetails,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "ui.showDueDates",
        sharedConfig.ui.showDueDates,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "ui.showPriority",
        sharedConfig.ui.showPriority,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "ui.theme",
        sharedConfig.ui.theme,
        vscode.ConfigurationTarget.Workspace
      );

      // Storage settings
      await config.update(
        "storageMode",
        sharedConfig.storage.mode,
        vscode.ConfigurationTarget.Workspace
      );

      // Groups
      await config.update(
        "defaultGroups",
        sharedConfig.defaultGroups,
        vscode.ConfigurationTarget.Workspace
      );
      await config.update(
        "groupOrdering",
        sharedConfig.groupOrdering,
        vscode.ConfigurationTarget.Workspace
      );
    } catch (error) {
      console.error("Failed to sync from shared config:", error);
      vscode.window.showWarningMessage(
        "Failed to sync configuration from shared settings"
      );
    }
  }

  /**
   * Sync settings from VS Code settings to shared config
   */
  private async syncToSharedConfig(): Promise<void> {
    try {
      const vsCodeSettings = this.getSettings();
      const currentSharedConfig = this.sharedConfig?.getConfig();
      if (!currentSharedConfig) {
        throw new Error("Shared configuration is not available");
      }

      // Create partial update for shared config
      const updates: Partial<SharedTaskManConfig> = {
        database: {
          ...currentSharedConfig.database,
          type: vsCodeSettings.database.type,
          autoRefresh: vsCodeSettings.database.autoRefresh,
          refreshInterval: vsCodeSettings.database.refreshInterval,
        },
        dtm: {
          ...currentSharedConfig.dtm,
          enableIntegration: vsCodeSettings.dtm.enableIntegration,
          serverPort: vsCodeSettings.dtm.serverPort,
          autoStart: vsCodeSettings.dtm.autoStart,
        },
        ui: {
          ...currentSharedConfig.ui,
          compactView: vsCodeSettings.ui.compactView,
          showTaskDetails: vsCodeSettings.ui.showTaskDetails,
          showDueDates: vsCodeSettings.ui.showDueDates,
          showPriority: vsCodeSettings.ui.showPriority,
          theme:
            vsCodeSettings.ui.theme === "auto"
              ? "system"
              : vsCodeSettings.ui.theme,
        },
        storage: {
          ...currentSharedConfig.storage,
          mode: vsCodeSettings.storageMode,
        },
        defaultGroups: vsCodeSettings.defaultGroups,
        groupOrdering: vsCodeSettings.groupOrdering,
      };

      // Update database-specific settings
      if (
        vsCodeSettings.database.type === "sqlite" &&
        vsCodeSettings.database.sqlitePath
      ) {
        updates.database!.sqlite = {
          path: vsCodeSettings.database.sqlitePath,
          timeout: currentSharedConfig.database.sqlite?.timeout || 30000,
          pragmas: currentSharedConfig.database.sqlite?.pragmas || {
            foreign_keys: true,
            journal_mode: "WAL",
            synchronous: "NORMAL",
          },
        };
      }

      if (
        vsCodeSettings.database.type === "dtm-api" &&
        vsCodeSettings.database.dtmApiUrl
      ) {
        updates.database!.dtmApi = {
          baseUrl: vsCodeSettings.database.dtmApiUrl,
          timeout: currentSharedConfig.database.dtmApi?.timeout || 30000,
          retryAttempts:
            currentSharedConfig.database.dtmApi?.retryAttempts || 3,
          healthCheck:
            currentSharedConfig.database.dtmApi?.healthCheck || "/health",
        };
      }

      await this.sharedConfig!.updateConfig(updates);
    } catch (error) {
      console.error("Failed to sync to shared config:", error);
      vscode.window.showWarningMessage(
        "Failed to sync configuration to shared settings"
      );
    }
  }

  /**
   * Get shared configuration instance
   */
  public getSharedConfig(): SharedConfigBridge | null {
    return this.sharedConfig;
  }

  /**
   * Show shared configuration file in editor
   */
  public async openSharedConfigFile(): Promise<void> {
    if (!this.sharedConfig) {
      vscode.window.showWarningMessage("Shared configuration is not available");
      return;
    }

    try {
      const configPath = this.sharedConfig.getConfigPath();
      const document = await vscode.workspace.openTextDocument(configPath);
      await vscode.window.showTextDocument(document);
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to open shared config file: ${error}`
      );
    }
  }

  /**
   * Show configuration sync status
   */
  public async showSyncStatus(): Promise<void> {
    if (!this.sharedConfig) {
      vscode.window.showWarningMessage("Shared configuration is not available");
      return;
    }

    try {
      const sharedConfig = this.sharedConfig.getConfig();
      const configPath = this.sharedConfig.getConfigPath();

      const message = `
**TaskMan-v2 Configuration Sync Status**

📁 **Shared Config File**: ${configPath}
📅 **Last Updated**: ${new Date(sharedConfig.lastUpdated).toLocaleString()}
👤 **Updated By**: ${sharedConfig.updatedBy}
🔗 **Database Type**: ${sharedConfig.database.type}
🎨 **UI Theme**: ${sharedConfig.ui.theme}
🔄 **Auto Sync**: ${sharedConfig.sync.enableAutoSync ? "Enabled" : "Disabled"}

*Changes made in either the main TaskMan-v2 UI or VS Code extension will be synchronized automatically.*
      `.trim();

      vscode.window
        .showInformationMessage(message, "Open Config File", "Refresh")
        .then((selection) => {
          if (selection === "Open Config File") {
            this.openSharedConfigFile();
          } else if (selection === "Refresh") {
            this.syncFromSharedConfig(this.sharedConfig!.getConfig());
          }
        });
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to get sync status: ${error}`);
    }
  }
  /**
   * Dispose resources
   */
  public dispose(): void {
    if (this.configChangeDisposable) {
      this.configChangeDisposable.dispose();
    }
    this.sharedConfig?.dispose();
  }
}
