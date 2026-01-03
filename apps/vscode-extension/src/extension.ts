import * as vscode from 'vscode';
import { ActionListProvider } from "./actionListProvider";
import { DatabaseService } from "./databaseService";
import { DTMSyncWorkflowService } from "./dtmWorkflowService";
import { E2ETestingService } from "./e2eTestingService";
import { TodoGroup, TodoItem } from "./models";
import { SettingsManager } from "./settingsManager";
import { StorageManager } from "./storageManager";
import { TodoTreeDataProvider } from "./todoTreeDataProvider";
import { TodoWebviewProvider } from "./todoWebviewProvider";

export function activate(context: vscode.ExtensionContext) {
  console.log("TaskMan-v2 extension is now active!");

  // Initialize storage manager
  const storageManager = new StorageManager(context);

  // Initialize settings manager
  const settingsManager = new SettingsManager();

  // Initialize database service
  const databaseService = new DatabaseService(context);

  // Initialize DTM sync workflow service
  const dtmWorkflowService = new DTMSyncWorkflowService(databaseService);

  // Initialize E2E testing service
  const e2eTestingService = new E2ETestingService(
    databaseService,
    settingsManager
  );
  dtmWorkflowService.setTestingService(e2eTestingService);

  // Initialize tree data provider
  const todoTreeProvider = new TodoTreeDataProvider(
    storageManager,
    databaseService
  );

  // Register tree views - both activity bar and explorer
  const treeView = vscode.window.createTreeView("taskman.view", {
    treeDataProvider: todoTreeProvider,
    showCollapseAll: true,
    canSelectMany: false,
  });

  const explorerTreeView = vscode.window.createTreeView("taskman.explorer", {
    treeDataProvider: todoTreeProvider,
    showCollapseAll: true,
    canSelectMany: false,
  });

  // Initialize action list provider
  const actionListProvider = new ActionListProvider(databaseService);

  // Register action list tree view
  const actionListTreeView = vscode.window.createTreeView("taskman.actionLists", {
    treeDataProvider: actionListProvider,
    showCollapseAll: true,
    canSelectMany: false,
  });

  // Initialize webview provider
  const webviewProvider = new TodoWebviewProvider(context, storageManager);

  // Register webview provider (only if webview details are enabled)
  const config = vscode.workspace.getConfiguration("taskman");
  let webviewDisposable: vscode.Disposable | undefined;

  if (config.get<boolean>("showWebviewDetails", true)) {
    webviewDisposable = vscode.window.registerWebviewViewProvider(
      "taskman.details",
      webviewProvider,
      {
        webviewOptions: {
          retainContextWhenHidden: true,
        },
      }
    );
  }

  // Command: Add Task
  const addTodoCommand = vscode.commands.registerCommand(
    "taskman.add",
    async (element?: TodoGroup) => {
      const title = await vscode.window.showInputBox({
        prompt: "Enter todo title",
        placeHolder: "Todo title...",
      });

      if (title) {
        let groupName = "Today"; // Default group

        if (element && element.contextValue === "group") {
          groupName =
            typeof element.label === "string"
              ? element.label
              : element.label?.label || "Today";
        } else {
          // Show group selection
          const groups = await storageManager.getGroups();
          const groupNames = groups.map((g) => g.name);

          if (groupNames.length > 1) {
            const selectedGroup = await vscode.window.showQuickPick(
              groupNames,
              {
                placeHolder: "Select group for the todo",
              }
            );
            if (selectedGroup) {
              groupName = selectedGroup;
            }
          }
        }

        const todoItem = new TodoItem(
          `todo-${Date.now()}`,
          title,
          false,
          groupName
        );

        await storageManager.addTodo(todoItem);
        todoTreeProvider.refresh();

        vscode.window.showInformationMessage(
          `Todo "${title}" added to ${groupName}`
        );
      }
    }
  );

  // Command: Edit Task
  const editTodoCommand = vscode.commands.registerCommand(
    "taskman.edit",
    async (element: TodoItem) => {
      if (element && element.contextValue === "todo") {
        const newTitle = await vscode.window.showInputBox({
          prompt: "Edit todo title",
          value: element.title,
        });

        if (newTitle && newTitle !== element.title) {
          element.title = newTitle;
          await storageManager.updateTodo(element);
          todoTreeProvider.refresh();

          vscode.window.showInformationMessage(`Todo updated to "${newTitle}"`);
        }
      }
    }
  );

  // Command: Toggle Task
  const toggleTodoCommand = vscode.commands.registerCommand(
    "taskman.toggle",
    async (element: TodoItem) => {
      if (element && element.contextValue === "todo") {
        element.completed = !element.completed;
        await storageManager.updateTodo(element);
        todoTreeProvider.refresh();

        const status = element.completed ? "completed" : "pending";
        vscode.window.showInformationMessage(
          `Todo "${element.title}" marked as ${status}`
        );
      }
    }
  );

  // Command: Delete Task
  const deleteTodoCommand = vscode.commands.registerCommand(
    "taskman.delete",
    async (element: TodoItem | TodoGroup) => {
      if (!element) {
        return;
      }

      const isGroup = element.contextValue === "group";
      const itemType = isGroup ? "group" : "todo";
      const itemName = isGroup
        ? (element as TodoGroup).name
        : (element as TodoItem).title;

      const result = await vscode.window.showWarningMessage(
        `Are you sure you want to delete this ${itemType}: "${itemName}"?`,
        { modal: true },
        "Delete"
      );

      if (result === "Delete") {
        if (isGroup) {
          await storageManager.deleteGroup((element as TodoGroup).name);
          vscode.window.showInformationMessage(`Group "${itemName}" deleted`);
        } else {
          await storageManager.deleteTodo((element as TodoItem).id);
          vscode.window.showInformationMessage(`Todo "${itemName}" deleted`);
        }
        todoTreeProvider.refresh();
      }
    }
  );

  // Command: Move Task
  const moveTodoCommand = vscode.commands.registerCommand(
    "taskman.move",
    async (element: TodoItem) => {
      if (element && element.contextValue === "todo") {
        const groups = await storageManager.getGroups();
        const groupNames = groups
          .map((g) => g.name)
          .filter((name) => name !== element.group);

        if (groupNames.length === 0) {
          vscode.window.showWarningMessage(
            "No other groups available to move to"
          );
          return;
        }

        const selectedGroup = await vscode.window.showQuickPick(groupNames, {
          placeHolder: `Move "${element.title}" to group...`,
        });

        if (selectedGroup) {
          const oldGroup = element.group;
          element.group = selectedGroup;
          await storageManager.updateTodo(element);
          todoTreeProvider.refresh();

          vscode.window.showInformationMessage(
            `Todo moved from "${oldGroup}" to "${selectedGroup}"`
          );
        }
      }
    }
  );

  // Command: Open Details
  const openDetailsCommand = vscode.commands.registerCommand(
    "taskman.openDetails",
    async (element: TodoItem) => {
      if (element && element.contextValue === "todo") {
        await webviewProvider.showTodoDetails(element);
      }
    }
  );

  // Command: Refresh
  const refreshCommand = vscode.commands.registerCommand(
    "taskman.refresh",
    () => {
      todoTreeProvider.refresh();
      vscode.window.showInformationMessage("Tasks refreshed");
    }
  );

  // Command: Add Group
  const addGroupCommand = vscode.commands.registerCommand(
    "taskman.addGroup",
    async () => {
      const groupName = await vscode.window.showInputBox({
        prompt: "Enter group name",
        placeHolder: "Group name...",
      });

      if (groupName) {
        const group = new TodoGroup(groupName);
        await storageManager.addGroup(group);
        todoTreeProvider.refresh();

        vscode.window.showInformationMessage(`Group "${groupName}" created`);
      }
    }
  );

  // Command: Open Settings
  const settingsCommand = vscode.commands.registerCommand(
    "taskman.settings",
    async () => {
      await settingsManager.showSettingsMenu();
    }
  );

  // Command: Refresh Action Lists
  const refreshActionListsCommand = vscode.commands.registerCommand(
    "taskman.refreshActionLists",
    () => {
      actionListProvider.refresh();
      vscode.window.showInformationMessage("Action lists refreshed");
    }
  );

  // Command: View Action List
  const viewActionListCommand = vscode.commands.registerCommand(
    "taskman.viewActionList",
    (item: any) => {
      // TODO: Show action list details in webview
      vscode.window.showInformationMessage(
        `Viewing action list: ${item.actionList.title}`
      );
    }
  );

  // Command: Toggle Action List Item
  const toggleActionListItemCommand = vscode.commands.registerCommand(
    "taskman.toggleActionListItem",
    async (item: any) => {
      try {
        await actionListProvider.toggleActionListItem(
          item.parentActionList.id,
          item.item.id
        );
        vscode.window.showInformationMessage(
          `Toggled: ${item.item.text}`
        );
      } catch (error) {
        vscode.window.showErrorMessage(
          `Failed to toggle item: ${error}`
        );
      }
    }
  );

  // Command: Load from Database
  const loadFromDatabaseCommand = vscode.commands.registerCommand(
    "taskman.loadFromDatabase",
    async () => {
      try {
        vscode.window.showInformationMessage("Loading data from database...");

        const data = await databaseService.loadAllData();

        if (
          data.projects.length > 0 ||
          data.sprints.length > 0 ||
          data.tasks.length > 0
        ) {
          // TODO: Convert database data to TodoItems and TodoGroups
          // For now, show a summary
          const message = `Loaded: ${data.projects.length} projects, ${data.sprints.length} sprints, ${data.tasks.length} tasks`;
          vscode.window.showInformationMessage(message);

          todoTreeProvider.refresh();
        } else {
          vscode.window.showWarningMessage("No data found in database");
        }
      } catch (error) {
        vscode.window.showErrorMessage(
          `Failed to load from database: ${error}`
        );
      }
    }
  );

  // Command: Enhanced DTM-TASKMAN Sync Workflow
  const syncWithDTMCommand = vscode.commands.registerCommand(
    "taskman.syncWithDTM",
    async () => {
      if (dtmWorkflowService.isWorkflowRunning()) {
        vscode.window.showWarningMessage(
          "DTM sync workflow is already running"
        );
        return;
      }

      try {
        // Show progress with cancellation support
        await vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "DTM-TASKMAN Sync Workflow",
            cancellable: false,
          },
          async (progress, token) => {
            // Set up progress callback
            dtmWorkflowService.setProgressCallback(
              (stage, stageProgress, message) => {
                progress.report({
                  increment: stageProgress / 4, // Divide by 4 stages
                  message: `[${stage.toUpperCase()}] ${message}`,
                });
              }
            );

            // Execute the complete sync workflow
            const result = await dtmWorkflowService.executeFullSyncWorkflow({
              includeCompleted: false,
              performanceMode: "thorough",
            });

            if (result.success) {
              const successMessage =
                `✅ DTM Sync Complete!\n` +
                `📊 ${result.metrics.totalTasks} tasks from ${result.metrics.totalProjects} projects\n` +
                `🏃 ${result.metrics.totalSprints} sprints organized into ${result.metrics.totalGroups} groups\n` +
                `⏱️ Completed in ${Math.round(result.duration / 1000)}s`;

              vscode.window.showInformationMessage(successMessage);

              // Refresh tree view to show synchronized data
              todoTreeProvider.refresh();
            } else {
              const errorMessage =
                `❌ DTM Sync Failed: ${result.message}\n` +
                `Errors: ${result.metrics.errors}, Warnings: ${result.metrics.warnings}`;

              vscode.window.showErrorMessage(errorMessage);

              // Show detailed error information in output channel
              const outputChannel =
                vscode.window.createOutputChannel("TaskMan DTM Sync");
              outputChannel.show();
              outputChannel.appendLine("=== DTM Sync Workflow Results ===");
              outputChannel.appendLine(`Success: ${result.success}`);
              outputChannel.appendLine(`Duration: ${result.duration}ms`);
              outputChannel.appendLine(`Message: ${result.message}`);

              if (result.errors.length > 0) {
                outputChannel.appendLine("\n=== Errors ===");
                result.errors.forEach((error, index) => {
                  outputChannel.appendLine(`${index + 1}. ${error}`);
                });
              }

              if (result.warnings.length > 0) {
                outputChannel.appendLine("\n=== Warnings ===");
                result.warnings.forEach((warning, index) => {
                  outputChannel.appendLine(`${index + 1}. ${warning}`);
                });
              }
            }
          }
        );
      } catch (error: any) {
        const errorMessage = `Failed to execute DTM sync workflow: ${
          error?.message || error
        }`;
        vscode.window.showErrorMessage(errorMessage);
        console.error("DTM sync workflow error:", error);
      }
    }
  );

  // Command: Connect Database
  const connectDatabaseCommand = vscode.commands.registerCommand(
    "taskman.connectDatabase",
    async () => {
      const settings = settingsManager.getSettings();
      const dbType = settings.database.type;

      try {
        const success = await databaseService.testConnection();

        if (success) {
          vscode.window.showInformationMessage(
            `Successfully connected to ${dbType} database`
          );
        } else {
          vscode.window.showErrorMessage(
            `Failed to connect to ${dbType} database`
          );
        }
      } catch (error) {
        vscode.window.showErrorMessage(`Database connection error: ${error}`);
      }
    }
  );

  // Command: Open Shared Config
  const openSharedConfigCommand = vscode.commands.registerCommand(
    "taskman.openSharedConfig",
    async () => {
      await settingsManager.openSharedConfigFile();
    }
  );

  // Command: Show Sync Status
  const showSyncStatusCommand = vscode.commands.registerCommand(
    "taskman.showSyncStatus",
    async () => {
      await settingsManager.showSyncStatus();
    }
  );

  // Command: Database Settings Menu
  const databaseSettingsCommand = vscode.commands.registerCommand(
    "taskman.databaseSettings",
    async () => {
      await settingsManager.showSettingsMenu();
    }
  );

  // Command: Test Database Connection
  const testConnectionCommand = vscode.commands.registerCommand(
    "taskman.testConnection",
    async () => {
      const settings = settingsManager.getSettings();
      if (settings.database.type === "local") {
        vscode.window.showInformationMessage(
          "✅ Local storage is always available"
        );
      } else {
        // Open the database settings menu which has the test connection option
        await settingsManager.showSettingsMenu();
      }
    }
  );

  // Command: Run End-to-End Tests on TaskMan
  const runE2ETestsCommand = vscode.commands.registerCommand(
    "taskman.runE2ETests",
    async () => {
      try {
        await vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "TaskMan End-to-End Testing",
            cancellable: false,
          },
          async (progress, token) => {
            // Set up progress callback
            e2eTestingService.setProgressCallback((testProgress, message) => {
              progress.report({
                increment: testProgress / 4, // Rough progress estimation
                message: message,
              });
            });

            // Run all test scenarios
            const results = await e2eTestingService.runAllTestScenarios();

            // Process and display results
            let totalTests = 0;
            let passedTests = 0;
            let failedTests = 0;
            const failedScenarios: string[] = [];

            for (const [scenarioId, result] of results) {
              totalTests++;
              if (result.success) {
                passedTests++;
              } else {
                failedTests++;
                failedScenarios.push(
                  `${scenarioId}: ${result.errors.join(", ")}`
                );
              }
            }

            // Show comprehensive results
            const outputChannel = vscode.window.createOutputChannel(
              "TaskMan E2E Test Results"
            );
            outputChannel.show();
            outputChannel.appendLine("=== TaskMan End-to-End Test Results ===");
            outputChannel.appendLine(`Total Scenarios: ${totalTests}`);
            outputChannel.appendLine(`Passed: ${passedTests}`);
            outputChannel.appendLine(`Failed: ${failedTests}`);
            outputChannel.appendLine(
              `Success Rate: ${Math.round((passedTests / totalTests) * 100)}%`
            );
            outputChannel.appendLine("");

            // Detailed results for each scenario
            for (const [scenarioId, result] of results) {
              outputChannel.appendLine(`=== ${scenarioId.toUpperCase()} ===`);
              outputChannel.appendLine(`Name: ${result.scenarioId}`);
              outputChannel.appendLine(
                `Success: ${result.success ? "✅" : "❌"}`
              );
              outputChannel.appendLine(`Duration: ${result.duration}ms`);
              outputChannel.appendLine(
                `Steps: ${result.metrics.passedSteps}/${result.metrics.totalSteps} passed`
              );

              if (result.errors.length > 0) {
                outputChannel.appendLine("Errors:");
                result.errors.forEach((error, index) => {
                  outputChannel.appendLine(`  ${index + 1}. ${error}`);
                });
              }

              if (result.warnings.length > 0) {
                outputChannel.appendLine("Warnings:");
                result.warnings.forEach((warning, index) => {
                  outputChannel.appendLine(`  ${index + 1}. ${warning}`);
                });
              }

              outputChannel.appendLine("");
            }

            // Show summary notification
            if (failedTests === 0) {
              vscode.window.showInformationMessage(
                `✅ All TaskMan E2E Tests Passed! (${passedTests}/${totalTests})`
              );
            } else {
              vscode.window.showWarningMessage(
                `⚠️ TaskMan E2E Tests: ${passedTests}/${totalTests} passed, ${failedTests} failed. Check output for details.`
              );
            }
          }
        );
      } catch (error: any) {
        vscode.window.showErrorMessage(
          `E2E Testing failed: ${error?.message || error}`
        );
        console.error("E2E Testing error:", error);
      }
    }
  );

  // Register tree selection event
  treeView.onDidChangeSelection(async (e) => {
    if (e.selection.length > 0) {
      const selected = e.selection[0];
      if (selected instanceof TodoItem) {
        await webviewProvider.showTodoDetails(selected);
      }
    }
  });

  // Add all disposables to context
  context.subscriptions.push(
    treeView,
    explorerTreeView,
    actionListTreeView,
    addTodoCommand,
    editTodoCommand,
    toggleTodoCommand,
    deleteTodoCommand,
    moveTodoCommand,
    openDetailsCommand,
    refreshCommand,
    addGroupCommand,
    settingsCommand,
    refreshActionListsCommand,
    viewActionListCommand,
    toggleActionListItemCommand,
    loadFromDatabaseCommand,
    syncWithDTMCommand,
    connectDatabaseCommand,
    openSharedConfigCommand,
    showSyncStatusCommand,
    databaseSettingsCommand,
    testConnectionCommand
  );

  // Add webview disposable if it exists
  if (webviewDisposable) {
    context.subscriptions.push(webviewDisposable);
  }

  // Listen for settings changes
  const settingsChangeListener = settingsManager.onConfigurationChanged(
    (settings: any) => {
      // Refresh tree view when settings change
      todoTreeProvider.refresh();

      // Update webview visibility if needed
      const showWebview = settings.showWebviewDetails;
      if (showWebview && !webviewDisposable) {
        // Enable webview if it was disabled
        webviewDisposable = vscode.window.registerWebviewViewProvider(
          "taskman.details",
          webviewProvider,
          {
            webviewOptions: {
              retainContextWhenHidden: true,
            },
          }
        );
        context.subscriptions.push(webviewDisposable);
      }
    }
  );

  context.subscriptions.push(settingsChangeListener);

  // Initialize default groups if none exist
  initializeDefaultGroups(storageManager, todoTreeProvider);
}

async function initializeDefaultGroups(
  storageManager: StorageManager,
  treeProvider: TodoTreeDataProvider
) {
  const groups = await storageManager.getGroups();

  if (groups.length === 0) {
    const config = vscode.workspace.getConfiguration("taskman");
    const defaultGroups = config.get<string[]>("defaultGroups", [
      "Today",
      "Upcoming",
      "Completed",
    ]);

    for (const groupName of defaultGroups) {
      const group = new TodoGroup(groupName);
      await storageManager.addGroup(group);
    }

    treeProvider.refresh();
  }
}

export function deactivate() {
    console.log('VS Code Todos extension is now deactivated');
}
