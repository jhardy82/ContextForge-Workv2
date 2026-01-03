import * as cp from "child_process";
import * as fs from "fs";
import fetch from "node-fetch";
import * as path from "path";
import * as vscode from "vscode";
import { ActionList, TodoGroup, TodoItem } from "./models";

export interface Project {
  id: string;
  name: string;
  status?: string;
  start_date?: string;
  target_end_date?: string;
  owner?: string;
  mission?: string;
}

export interface Sprint {
  id: string;
  name: string;
  goal?: string;
  start_date?: string;
  end_date?: string;
  status?: string;
  project_id: string;
}

export interface Task {
  id: string;
  title: string;
  status?: string;
  priority?: string;
  severity?: string;
  estimate_points?: number;
  actual_hours?: number;
  description?: string;
  created_at?: string;
  updated_at?: string;
  due_date?: string;
  sprint_id?: string;
  project_id?: string;
  owner?: string;
}

export interface DatabaseConnection {
  type: "sqlite" | "dtm-api" | "local";
  isConnected: boolean;
  lastError?: string;
}

export class DatabaseService {
  private connection: DatabaseConnection = {
    type: "local",
    isConnected: false,
  };

  constructor(private context: vscode.ExtensionContext) {}

  /**
   * Get current connection status
   */
  getConnectionStatus(): DatabaseConnection {
    return { ...this.connection };
  }

  /**
   * Connect to database based on configuration
   */
  async connect(): Promise<boolean> {
    const config = vscode.workspace.getConfiguration("taskman");
    const dbType = config.get<string>("database.type", "local");

    try {
      switch (dbType) {
        case "sqlite":
          return await this.connectToSQLite();
        case "dtm-api":
          return await this.connectToDTMApi();
        default:
          this.connection = { type: "local", isConnected: true };
          return true;
      }
    } catch (error) {
      this.connection.lastError =
        error instanceof Error ? error.message : "Unknown error";
      this.connection.isConnected = false;
      return false;
    }
  }

  /**
   * Connect to SQLite database
   */
  private async connectToSQLite(): Promise<boolean> {
    const config = vscode.workspace.getConfiguration("taskman");
    const sqlitePath = config.get<string>(
      "database.sqlitePath",
      "db/trackers.sqlite"
    );

    // Get workspace root
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
      throw new Error("No workspace folder found");
    }

    const fullPath = path.resolve(workspaceRoot, sqlitePath);

    // Check if SQLite file exists
    if (!fs.existsSync(fullPath)) {
      throw new Error(`SQLite database not found at: ${fullPath}`);
    }

    // For now, we'll just verify the file exists
    // In a real implementation, you'd use a SQLite library like sqlite3
    this.connection = {
      type: "sqlite",
      isConnected: true,
    };

    vscode.window.showInformationMessage(
      `Connected to SQLite database: ${fullPath}`
    );
    return true;
  }

  /**
   * Connect to DTM API
   */
  private async connectToDTMApi(): Promise<boolean> {
    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    try {
      // Test DTM API connection
      const response = await fetch(`${apiUrl}/health`);
      if (!response.ok) {
        throw new Error(`DTM API not responding: ${response.status}`);
      }

      this.connection = {
        type: "dtm-api",
        isConnected: true,
      };

      vscode.window.showInformationMessage(`Connected to DTM API: ${apiUrl}`);
      return true;
    } catch (error) {
      throw new Error(`Failed to connect to DTM API: ${apiUrl}`);
    }
  }

  /**
   * Load projects from database
   */
  async loadProjects(): Promise<Project[]> {
    if (!this.connection.isConnected) {
      await this.connect();
    }

    switch (this.connection.type) {
      case "sqlite":
        return await this.loadProjectsFromSQLite();
      case "dtm-api":
        return await this.loadProjectsFromDTM();
      default:
        return [];
    }
  }

  /**
   * Load sprints from database
   */
  async loadSprints(projectId?: string): Promise<Sprint[]> {
    if (!this.connection.isConnected) {
      await this.connect();
    }

    switch (this.connection.type) {
      case "sqlite":
        return await this.loadSprintsFromSQLite(projectId);
      case "dtm-api":
        return await this.loadSprintsFromDTM(projectId);
      default:
        return [];
    }
  }

  /**
   * Load tasks from database
   */
  async loadTasks(sprintId?: string, projectId?: string): Promise<Task[]> {
    if (!this.connection.isConnected) {
      await this.connect();
    }

    switch (this.connection.type) {
      case "sqlite":
        return await this.loadTasksFromSQLite(sprintId, projectId);
      case "dtm-api":
        return await this.loadTasksFromDTM(sprintId, projectId);
      default:
        return [];
    }
  }

  /**
   * Load action lists from database
   */
  async loadActionLists(
    projectId?: string,
    sprintId?: string,
    status?: string
  ): Promise<ActionList[]> {
    if (!this.connection.isConnected) {
      await this.connect();
    }

    switch (this.connection.type) {
      case "sqlite":
        return await this.loadActionListsFromSQLite(
          projectId,
          sprintId,
          status
        );
      case "dtm-api":
        return await this.loadActionListsFromDTM(projectId, sprintId, status);
      default:
        return [];
    }
  }

  /**
   * Load projects from SQLite database
   */
  private async loadProjectsFromSQLite(): Promise<Project[]> {
    try {
      const data = await this.loadFromSQLite();
      return data.projects;
    } catch (error) {
      console.error(`Error loading projects from SQLite: ${error}`);
      return [];
    }
  }

  /**
   * Load sprints from SQLite database
   */
  private async loadSprintsFromSQLite(projectId?: string): Promise<Sprint[]> {
    try {
      const data = await this.loadFromSQLite();
      let sprints = data.sprints;

      if (projectId) {
        sprints = sprints.filter((s) => s.project_id === projectId);
      }

      return sprints;
    } catch (error) {
      console.error(`Error loading sprints from SQLite: ${error}`);
      return [];
    }
  }

  /**
   * Load tasks from SQLite database
   */
  private async loadTasksFromSQLite(
    sprintId?: string,
    projectId?: string
  ): Promise<Task[]> {
    try {
      const data = await this.loadFromSQLite();
      let tasks = data.tasks;

      if (projectId) {
        tasks = tasks.filter((t) => t.project_id === projectId);
      }

      if (sprintId) {
        tasks = tasks.filter((t) => t.sprint_id === sprintId);
      }

      return tasks;
    } catch (error) {
      console.error(`Error loading tasks from SQLite: ${error}`);
      return [];
    }
  }

  /**
   * Load projects from DTM API
   */
  private async loadProjectsFromDTM(): Promise<Project[]> {
    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    try {
      const response = await fetch(`${apiUrl}/projects/`);
      if (!response.ok) {
        throw new Error(`Failed to load projects: ${response.status}`);
      }

      const result: any = await response.json();
      const projects: Project[] = result.data || result;
      vscode.window.showInformationMessage(
        `Loaded ${projects.length} projects from DTM API`
      );
      return projects;
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to load projects from DTM API: ${error}`
      );
      return [];
    }
  }

  /**
   * Load sprints from DTM API
   */
  private async loadSprintsFromDTM(projectId?: string): Promise<Sprint[]> {
    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    const url = projectId
      ? `${apiUrl}/sprints/?project_id=${projectId}`
      : `${apiUrl}/sprints/`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to load sprints: ${response.status}`);
      }

      const result: any = await response.json();
      const sprints: Sprint[] = result.data || result;
      vscode.window.showInformationMessage(
        `Loaded ${sprints.length} sprints from DTM API`
      );
      return sprints;
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to load sprints from DTM API: ${error}`
      );
      return [];
    }
  }

  /**
   * Load tasks from DTM API
   */
  private async loadTasksFromDTM(
    sprintId?: string,
    projectId?: string
  ): Promise<Task[]> {
    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    let url = `${apiUrl}/tasks/`;
    const params = new URLSearchParams();

    if (sprintId) {
      params.append("sprint_id", sprintId);
    }
    if (projectId) {
      params.append("project_id", projectId);
    }

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to load tasks: ${response.status}`);
      }

      const result: any = await response.json();
      const tasks: Task[] = result.data || result;
      vscode.window.showInformationMessage(
        `Loaded ${tasks.length} tasks from DTM API`
      );
      return tasks;
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to load tasks from DTM API: ${error}`
      );
      return [];
    }
  }

  /**
   * Load action lists from SQLite database
   */
  private async loadActionListsFromSQLite(
    projectId?: string,
    sprintId?: string,
    status?: string
  ): Promise<ActionList[]> {
    // Action lists are PostgreSQL-only, not in SQLite
    vscode.window.showWarningMessage(
      "Action lists are not available in SQLite database. Please use DTM API mode."
    );
    return [];
  }

  /**
   * Load action lists from DTM API
   */
  private async loadActionListsFromDTM(
    projectId?: string,
    sprintId?: string,
    status?: string
  ): Promise<ActionList[]> {
    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    let url = `${apiUrl}/action-lists/`;
    const params = new URLSearchParams();

    if (projectId) {
      params.append("project_id", projectId);
    }
    if (sprintId) {
      params.append("sprint_id", sprintId);
    }
    if (status) {
      params.append("status", status);
    }

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to load action lists: ${response.status}`);
      }

      const result: any = await response.json();
      const actionLists: ActionList[] =
        result.data || result.action_lists || result;
      vscode.window.showInformationMessage(
        `Loaded ${actionLists.length} action lists from DTM API`
      );
      return actionLists;
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to load action lists from DTM API: ${error}`
      );
      return [];
    }
  }

  /**
   * Convert database tasks to TodoItems for the TreeView
   */
  convertTasksToTodoItems(tasks: Task[]): TodoItem[] {
    return tasks.map(
      (task) =>
        new TodoItem(
          task.id,
          task.title,
          task.status === "completed",
          this.getGroupForTask(task),
          task.description,
          task.due_date,
          this.getTagsForTask(task)
        )
    );
  }

  /**
   * Convert database tasks to TodoGroups organized by project/sprint
   */
  async convertTasksToGroups(
    projects: Project[],
    sprints: Sprint[],
    tasks: Task[]
  ): Promise<TodoGroup[]> {
    const groups: TodoGroup[] = [];

    for (const project of projects) {
      const projectGroup = new TodoGroup(project.name);
      const projectSprints = sprints.filter((s) => s.project_id === project.id);

      for (const sprint of projectSprints) {
        const sprintTasks = tasks.filter((t) => t.sprint_id === sprint.id);
        if (sprintTasks.length > 0) {
          const sprintTodoItems = this.convertTasksToTodoItems(sprintTasks);
          const sprintGroup = new TodoGroup(
            `${sprint.name} (${sprintTasks.length} tasks)`,
            sprintTodoItems
          );
          groups.push(sprintGroup);
        }
      }

      // Add ungrouped project tasks
      const ungroupedTasks = tasks.filter(
        (t) => t.project_id === project.id && !t.sprint_id
      );
      if (ungroupedTasks.length > 0) {
        const ungroupedTodoItems = this.convertTasksToTodoItems(ungroupedTasks);
        const ungroupedGroup = new TodoGroup(
          `${project.name} - Other (${ungroupedTasks.length} tasks)`,
          ungroupedTodoItems
        );
        groups.push(ungroupedGroup);
      }
    }

    return groups;
  }

  /**
   * Determine the appropriate group for a task
   */
  private getGroupForTask(task: Task): string {
    if (task.status === "completed") {
      return "Completed";
    } else if (task.due_date && new Date(task.due_date) <= new Date()) {
      return "Overdue";
    } else if (task.priority === "high" || task.priority === "urgent") {
      return "High Priority";
    } else {
      return "Active Tasks";
    }
  }

  /**
   * Generate tags for a task based on its properties
   */
  private getTagsForTask(task: Task): string[] {
    const tags: string[] = [];

    if (task.priority) {
      tags.push(`priority:${task.priority}`);
    }

    if (task.status) {
      tags.push(`status:${task.status}`);
    }

    if (task.project_id) {
      tags.push(`project:${task.project_id}`);
    }

    if (task.sprint_id) {
      tags.push(`sprint:${task.sprint_id}`);
    }

    return tags;
  }

  /**
   * Test database connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.connect();
      if (this.connection.isConnected) {
        vscode.window.showInformationMessage(
          `✅ Database connection successful (${this.connection.type})`
        );
        return true;
      } else {
        vscode.window.showErrorMessage(
          `❌ Database connection failed: ${this.connection.lastError}`
        );
        return false;
      }
    } catch (error) {
      vscode.window.showErrorMessage(`❌ Database connection failed: ${error}`);
      return false;
    }
  }

  /**
   * Disconnect from database
   */
  disconnect(): void {
    this.connection.isConnected = false;
    this.connection.lastError = undefined;
  }

  /**
   * Load all data from configured database
   */
  async loadAllData(): Promise<{
    projects: Project[];
    sprints: Sprint[];
    tasks: Task[];
  }> {
    const config = vscode.workspace.getConfiguration("taskman");
    const dbType = config.get<string>("database.type", "local");

    switch (dbType) {
      case "sqlite":
        return this.loadFromSQLite();
      case "dtm-api":
        return this.loadFromDTMAPI();
      case "local":
      default:
        // Return empty data for local storage mode
        return { projects: [], sprints: [], tasks: [] };
    }
  }

  /**
   * Load data from DTM API
   */
  async loadFromDTMAPI(): Promise<{
    projects: Project[];
    sprints: Sprint[];
    tasks: Task[];
  }> {
    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3000/api"
    );

    try {
      const [projectsResponse, sprintsResponse, tasksResponse] =
        await Promise.all([
          fetch(`${apiUrl}/projects`),
          fetch(`${apiUrl}/sprints`),
          fetch(`${apiUrl}/tasks`),
        ]);

      const projects: Project[] = projectsResponse.ok
        ? await projectsResponse.json()
        : [];
      const sprints: Sprint[] = sprintsResponse.ok
        ? await sprintsResponse.json()
        : [];
      const tasks: Task[] = tasksResponse.ok ? await tasksResponse.json() : [];

      return { projects, sprints, tasks };
    } catch (error) {
      throw new Error(`Failed to load from DTM API: ${error}`);
    }
  }

  /**
   * Load data from SQLite database
   */
  async loadFromSQLite(): Promise<{
    projects: Project[];
    sprints: Sprint[];
    tasks: Task[];
  }> {
    const config = vscode.workspace.getConfiguration("taskman");
    const dbPath = config.get<string>(
      "database.sqlitePath",
      "db/trackers.sqlite"
    );

    // Resolve workspace path
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
      return { projects: [], sprints: [], tasks: [] };
    }

    const rootPath = workspaceFolders[0].uri.fsPath;
    const fullDbPath = path.isAbsolute(dbPath)
      ? dbPath
      : path.join(rootPath, dbPath);

    // Assuming python folder is at the root of the extension
    const scriptPath = path.join(__dirname, "..", "python", "sqlite_bridge.py");

    return new Promise((resolve, reject) => {
      // Use the workspace python interpreter if available, or default to python
      const pythonCmd = "python";

      cp.exec(
        `"${pythonCmd}" "${scriptPath}" "${fullDbPath}"`,
        (err, stdout, stderr) => {
          if (err) {
            console.error(`SQLite load error: ${err.message}`);
            // Fallback to empty if python script fails (e.g. python not installed)
            vscode.window.showErrorMessage(`SQLite load error: ${err.message}`);
            resolve({ projects: [], sprints: [], tasks: [] });
            return;
          }

          try {
            const result = JSON.parse(stdout);
            if (result.error) {
              vscode.window.showErrorMessage(`SQLite error: ${result.error}`);
              resolve({ projects: [], sprints: [], tasks: [] });
              return;
            }

            resolve({
              projects: result.projects || [],
              sprints: result.sprints || [],
              tasks: result.tasks || [],
            });
          } catch (parseErr) {
            console.error(`Failed to parse SQLite result: ${parseErr}`);
            vscode.window.showErrorMessage(
              `Failed to parse SQLite result: ${parseErr}`
            );
            resolve({ projects: [], sprints: [], tasks: [] });
          }
        }
      );
    });
  }

  /**
   * Toggle action list item completion via DTM API
   */
  async toggleActionListItem(
    actionListId: string,
    itemId: string,
    completed: boolean
  ): Promise<void> {
    if (this.connection.type !== "dtm-api") {
      vscode.window.showWarningMessage(
        "Action list updates require DTM API mode."
      );
      return;
    }

    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    const url = `${apiUrl}/action-lists/${actionListId}/items/${itemId}/toggle`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ completed }),
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle item: ${response.status}`);
      }
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to toggle action list item via DTM API: ${error}`
      );
      throw error;
    }
  }

  /**
   * Create action list via DTM API
   */
  async createActionList(actionList: Partial<ActionList>): Promise<ActionList> {
    if (this.connection.type !== "dtm-api") {
      throw new Error("Action list creation requires DTM API mode.");
    }

    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    const url = `${apiUrl}/action-lists/`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(actionList),
      });

      if (!response.ok) {
        throw new Error(`Failed to create action list: ${response.status}`);
      }

      const result: any = await response.json();
      return result.data || result;
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to create action list via DTM API: ${error}`
      );
      throw error;
    }
  }

  /**
   * Delete action list via DTM API
   */
  async deleteActionList(id: string): Promise<void> {
    if (this.connection.type !== "dtm-api") {
      throw new Error("Action list deletion requires DTM API mode.");
    }

    const config = vscode.workspace.getConfiguration("taskman");
    const apiUrl = config.get<string>(
      "database.dtmApiUrl",
      "http://localhost:3001/api/v1"
    );

    const url = `${apiUrl}/action-lists/${id}`;

    try {
      const response = await fetch(url, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Failed to delete action list: ${response.status}`);
      }
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to delete action list via DTM API: ${error}`
      );
      throw error;
    }
  }
}
