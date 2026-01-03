import * as vscode from 'vscode';
import {
  SchemaMigration,
  TodoGroup,
  TodoItem,
  TodoStorageData,
} from "./models";

export class StorageManager {
  private static readonly STORAGE_KEY = "taskman.data";
  private static readonly CURRENT_VERSION = 1;

  constructor(private context: vscode.ExtensionContext) {}

  /**
   * Get the appropriate storage based on configuration
   */
  private getStorage(): vscode.Memento {
    const config = vscode.workspace.getConfiguration("todos");
    const storageMode = config.get<string>("storageMode", "workspace");

    return storageMode === "global"
      ? this.context.globalState
      : this.context.workspaceState;
  }

  /**
   * Load all data from storage
   */
  private async loadData(): Promise<TodoStorageData> {
    const storage = this.getStorage();
    const rawData = await storage.get(StorageManager.STORAGE_KEY);

    if (!rawData) {
      return {
        version: StorageManager.CURRENT_VERSION,
        todos: [],
        groups: [],
      };
    }

    // Apply schema migrations
    return SchemaMigration.migrate(rawData);
  }

  /**
   * Save all data to storage
   */
  private async saveData(data: TodoStorageData): Promise<void> {
    const storage = this.getStorage();
    data.version = StorageManager.CURRENT_VERSION;
    await storage.update(StorageManager.STORAGE_KEY, data);
  }

  /**
   * Get all todos
   */
  async getTodos(): Promise<TodoItem[]> {
    const data = await this.loadData();
    return data.todos.map((todo) => TodoItem.fromStorageObject(todo));
  }

  /**
   * Get todos by group
   */
  async getTodosByGroup(groupName: string): Promise<TodoItem[]> {
    const todos = await this.getTodos();
    return todos.filter((todo) => todo.group === groupName);
  }

  /**
   * Get all groups with their todos
   */
  async getGroups(): Promise<TodoGroup[]> {
    const data = await this.loadData();
    const todos = data.todos.map((todo) => TodoItem.fromStorageObject(todo));

    // Create groups with their todos
    const groupMap = new Map<string, TodoItem[]>();

    // Initialize groups from storage
    data.groups.forEach((group) => {
      groupMap.set(group.name, []);
    });

    // Assign todos to groups
    todos.forEach((todo) => {
      if (!groupMap.has(todo.group)) {
        groupMap.set(todo.group, []);
      }
      groupMap.get(todo.group)!.push(todo);
    });

    // Convert to TodoGroup objects
    const groups: TodoGroup[] = [];
    for (const [groupName, groupTodos] of groupMap) {
      const groupData = data.groups.find((g) => g.name === groupName);
      if (groupData) {
        groups.push(TodoGroup.fromStorageObject(groupData, groupTodos));
      } else {
        // Create group if it doesn't exist in storage (for orphaned todos)
        groups.push(new TodoGroup(groupName, groupTodos));
      }
    }

    // Sort groups according to configuration
    const config = vscode.workspace.getConfiguration("todos");
    const groupOrdering = config.get<string[]>("groupOrdering", [
      "Today",
      "Upcoming",
      "Completed",
    ]);

    return groups.sort((a, b) => {
      const aIndex = groupOrdering.indexOf(a.name);
      const bIndex = groupOrdering.indexOf(b.name);

      // If both are in ordering list, sort by order
      if (aIndex !== -1 && bIndex !== -1) {
        return aIndex - bIndex;
      }

      // If only one is in ordering list, prioritize it
      if (aIndex !== -1) {
        return -1;
      }
      if (bIndex !== -1) {
        return 1;
      }

      // If neither is in ordering list, sort alphabetically
      return a.name.localeCompare(b.name);
    });
  }

  /**
   * Add a new todo
   */
  async addTodo(todo: TodoItem): Promise<void> {
    const data = await this.loadData();

    // Ensure the group exists
    if (!data.groups.some((g) => g.name === todo.group)) {
      data.groups.push(new TodoGroup(todo.group).toStorageObject());
    }

    data.todos.push(todo.toStorageObject());
    await this.saveData(data);
  }

  /**
   * Update an existing todo
   */
  async updateTodo(todo: TodoItem): Promise<void> {
    const data = await this.loadData();
    const index = data.todos.findIndex((t) => t.id === todo.id);

    if (index !== -1) {
      const updatedTodo = todo.toStorageObject();
      updatedTodo.updatedAt = new Date().toISOString();
      data.todos[index] = updatedTodo;

      // Ensure the group exists if it was changed
      if (!data.groups.some((g) => g.name === todo.group)) {
        data.groups.push(new TodoGroup(todo.group).toStorageObject());
      }

      await this.saveData(data);
    }
  }

  /**
   * Delete a todo
   */
  async deleteTodo(todoId: string): Promise<void> {
    const data = await this.loadData();
    data.todos = data.todos.filter((t) => t.id !== todoId);
    await this.saveData(data);
  }

  /**
   * Add a new group
   */
  async addGroup(group: TodoGroup): Promise<void> {
    const data = await this.loadData();

    // Check if group already exists
    if (!data.groups.some((g) => g.name === group.name)) {
      data.groups.push(group.toStorageObject());
      await this.saveData(data);
    }
  }

  /**
   * Delete a group and all its todos
   */
  async deleteGroup(groupName: string): Promise<void> {
    const data = await this.loadData();

    // Remove all todos in the group
    data.todos = data.todos.filter((t) => t.group !== groupName);

    // Remove the group
    data.groups = data.groups.filter((g) => g.name !== groupName);

    await this.saveData(data);
  }

  /**
   * Get statistics
   */
  async getStatistics(): Promise<{
    totalTodos: number;
    completedTodos: number;
    pendingTodos: number;
    overdueTodos: number;
    todayTodos: number;
  }> {
    const todos = await this.getTodos();
    const now = new Date();
    const today = now.toDateString();

    const stats = {
      totalTodos: todos.length,
      completedTodos: todos.filter((t) => t.completed).length,
      pendingTodos: todos.filter((t) => !t.completed).length,
      overdueTodos: 0,
      todayTodos: 0,
    };

    for (const todo of todos) {
      if (todo.dueDate) {
        const dueDate = new Date(todo.dueDate);

        if (dueDate.toDateString() === today) {
          stats.todayTodos++;
        }

        if (dueDate < now && !todo.completed) {
          stats.overdueTodos++;
        }
      }
    }

    return stats;
  }

  /**
   * Export todos to JSON
   */
  async exportTodos(): Promise<string> {
    const data = await this.loadData();
    return JSON.stringify(data, null, 2);
  }

  /**
   * Import todos from JSON
   */
  async importTodos(
    jsonData: string,
    mergeMode: boolean = false
  ): Promise<void> {
    try {
      const importedData = JSON.parse(jsonData) as TodoStorageData;
      const migratedData = SchemaMigration.migrate(importedData);

      if (mergeMode) {
        const currentData = await this.loadData();

        // Merge groups (avoid duplicates)
        const existingGroupNames = new Set(
          currentData.groups.map((g) => g.name)
        );
        migratedData.groups.forEach((group) => {
          if (!existingGroupNames.has(group.name)) {
            currentData.groups.push(group);
          }
        });

        // Merge todos (avoid ID conflicts)
        const existingTodoIds = new Set(currentData.todos.map((t) => t.id));
        migratedData.todos.forEach((todo) => {
          if (!existingTodoIds.has(todo.id)) {
            currentData.todos.push(todo);
          } else {
            // Generate new ID for conflicting todos
            todo.id = `todo-${Date.now()}-${Math.random()
              .toString(36)
              .substr(2, 9)}`;
            currentData.todos.push(todo);
          }
        });

        await this.saveData(currentData);
      } else {
        // Replace all data
        await this.saveData(migratedData);
      }
    } catch (error) {
      throw new Error(
        `Failed to import todos: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }

  /**
   * Clear all data (with confirmation)
   */
  async clearAllData(): Promise<void> {
    const emptyData: TodoStorageData = {
      version: StorageManager.CURRENT_VERSION,
      todos: [],
      groups: [],
    };

    await this.saveData(emptyData);
  }
}
