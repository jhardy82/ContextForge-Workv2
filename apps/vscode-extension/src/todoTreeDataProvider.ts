import * as vscode from 'vscode';
import { DatabaseService } from "./databaseService";
import { TodoGroup, TodoItem } from "./models";
import { StorageManager } from './storageManager';

export class TodoTreeDataProvider
  implements vscode.TreeDataProvider<TodoItem | TodoGroup>
{
  private _onDidChangeTreeData: vscode.EventEmitter<
    TodoItem | TodoGroup | undefined | null | void
  > = new vscode.EventEmitter<TodoItem | TodoGroup | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<
    TodoItem | TodoGroup | undefined | null | void
  > = this._onDidChangeTreeData.event;

  constructor(
    private storageManager: StorageManager,
    private databaseService?: DatabaseService
  ) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: TodoItem | TodoGroup): vscode.TreeItem {
    return element;
  }

  async getChildren(
    element?: TodoItem | TodoGroup
  ): Promise<(TodoItem | TodoGroup)[]> {
    if (!element) {
      // Root level - return groups
      return this.getRootElements();
    }

    if (element instanceof TodoGroup) {
      // Return todos in this group
      return this.getTodosInGroup(element);
    }

    // TodoItem has no children
    return [];
  }

  private async getRootElements(): Promise<TodoGroup[]> {
    try {
      let groups: TodoGroup[] = [];

      // Check if we should use DatabaseService
      const taskmanConfig = vscode.workspace.getConfiguration("taskman");
      const dbType = taskmanConfig.get<string>("database.type", "local");

      if (
        this.databaseService &&
        (dbType === "sqlite" || dbType === "dtm-api")
      ) {
        const data = await this.databaseService.loadAllData();
        groups = await this.databaseService.convertTasksToGroups(
          data.projects,
          data.sprints,
          data.tasks
        );
      } else {
        groups = await this.storageManager.getGroups();
      }

      if (groups.length === 0) {
        // Return empty state indicator
        return [];
      }

      // Filter out empty groups based on configuration
      const config = vscode.workspace.getConfiguration("todos");
      const hideEmptyGroups = config.get<boolean>("hideEmptyGroups", false);

      if (hideEmptyGroups) {
        return groups.filter((group) => group.todos.length > 0);
      }

      return groups;
    } catch (error) {
      console.error("Error getting root elements:", error);
      vscode.window.showErrorMessage(
        `Failed to load todos: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
      return [];
    }
  }

  private async getTodosInGroup(group: TodoGroup): Promise<TodoItem[]> {
    try {
      let todos: TodoItem[] = [];

      // Check if we should use DatabaseService
      const taskmanConfig = vscode.workspace.getConfiguration("taskman");
      const dbType = taskmanConfig.get<string>("database.type", "local");

      if (
        this.databaseService &&
        (dbType === "sqlite" || dbType === "dtm-api")
      ) {
        // For DatabaseService, todos are already in the group
        todos = group.todos;
      } else {
        todos = await this.storageManager.getTodosByGroup(group.name);
      }

      // Sort todos within group
      const config = vscode.workspace.getConfiguration("todos");
      const sortBy = config.get<string>("sortBy", "created");
      const sortOrder = config.get<string>("sortOrder", "asc");

      return this.sortTodos(todos, sortBy, sortOrder);
    } catch (error) {
      console.error("Error getting todos in group:", error);
      vscode.window.showErrorMessage(
        `Failed to load todos in group "${group.name}": ${
          error instanceof Error ? error.message : String(error)
        }`
      );
      return [];
    }
  }

  private sortTodos(
    todos: TodoItem[],
    sortBy: string,
    sortOrder: string
  ): TodoItem[] {
    const multiplier = sortOrder === "desc" ? -1 : 1;

    return todos.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "title":
          comparison = a.title.localeCompare(b.title);
          break;

        case "completed":
          // Incomplete todos first, then completed
          comparison = (a.completed ? 1 : 0) - (b.completed ? 1 : 0);
          break;

        case "dueDate":
          if (a.dueDate && b.dueDate) {
            comparison =
              new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
          } else if (a.dueDate) {
            comparison = -1; // a has due date, b doesn't - a comes first
          } else if (b.dueDate) {
            comparison = 1; // b has due date, a doesn't - b comes first
          }
          break;

        case "priority":
          // If we had priority field, we'd sort by it here
          // For now, sort by completion status then title
          comparison = (a.completed ? 1 : 0) - (b.completed ? 1 : 0);
          if (comparison === 0) {
            comparison = a.title.localeCompare(b.title);
          }
          break;

        case "created":
        default:
          // Sort by ID which contains timestamp
          const aTime = this.extractTimestampFromId(a.id);
          const bTime = this.extractTimestampFromId(b.id);
          comparison = aTime - bTime;
          break;
      }

      return comparison * multiplier;
    });
  }

  private extractTimestampFromId(id: string): number {
    // Extract timestamp from ID format "todo-{timestamp}-{random}" or "todo-{timestamp}"
    const parts = id.split("-");
    if (parts.length >= 2) {
      const timestamp = parseInt(parts[1], 10);
      if (!isNaN(timestamp)) {
        return timestamp;
      }
    }
    return 0;
  }

  /**
   * Get parent of an element (for reveal functionality)
   */
  getParent(
    element: TodoItem | TodoGroup
  ): vscode.ProviderResult<TodoItem | TodoGroup> {
    if (element instanceof TodoItem) {
      // Find the group this todo belongs to
      return this.storageManager.getGroups().then((groups) => {
        return groups.find((group) => group.name === element.group);
      });
    }

    // Groups have no parent (they are root elements)
    return undefined;
  }

  /**
   * Reveal a specific todo item in the tree
   */
  async revealTodo(todoId: string): Promise<void> {
    try {
      const todos = await this.storageManager.getTodos();
      const todo = todos.find((t) => t.id === todoId);

      if (todo) {
        // Refresh to ensure tree is up to date
        this.refresh();

        // The tree view would need to be passed in to actually reveal
        // This is typically done from the extension activation
        vscode.commands.executeCommand("todos.view.reveal", todo, {
          select: true,
          focus: true,
          expand: true,
        });
      }
    } catch (error) {
      console.error("Error revealing todo:", error);
    }
  }

  /**
   * Filter todos based on search criteria
   */
  async searchTodos(query: string): Promise<TodoItem[]> {
    try {
      const todos = await this.storageManager.getTodos();
      const lowerQuery = query.toLowerCase();

      return todos.filter((todo) => {
        // Search in title
        if (todo.title.toLowerCase().includes(lowerQuery)) {
          return true;
        }

        // Search in description
        if (
          todo.description &&
          todo.description.toLowerCase().includes(lowerQuery)
        ) {
          return true;
        }

        // Search in tags
        if (
          todo.tags &&
          todo.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))
        ) {
          return true;
        }

        // Search in group
        if (todo.group.toLowerCase().includes(lowerQuery)) {
          return true;
        }

        return false;
      });
    } catch (error) {
      console.error("Error searching todos:", error);
      return [];
    }
  }

  /**
   * Get todos due today
   */
  async getTodosDueToday(): Promise<TodoItem[]> {
    try {
      const todos = await this.storageManager.getTodos();
      const today = new Date().toDateString();

      return todos.filter((todo) => {
        if (!todo.dueDate || todo.completed) {
          return false;
        }

        const dueDate = new Date(todo.dueDate);
        return dueDate.toDateString() === today;
      });
    } catch (error) {
      console.error("Error getting todos due today:", error);
      return [];
    }
  }

  /**
   * Get overdue todos
   */
  async getOverdueTodos(): Promise<TodoItem[]> {
    try {
      const todos = await this.storageManager.getTodos();
      const now = new Date();

      return todos.filter((todo) => {
        if (!todo.dueDate || todo.completed) {
          return false;
        }

        const dueDate = new Date(todo.dueDate);
        return dueDate < now;
      });
    } catch (error) {
      console.error("Error getting overdue todos:", error);
      return [];
    }
  }
}
