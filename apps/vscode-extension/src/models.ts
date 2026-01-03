import * as vscode from 'vscode';

export class TodoItem extends vscode.TreeItem {
  constructor(
    public readonly id: string,
    public title: string,
    public completed: boolean,
    public group: string,
    public description?: string,
    public dueDate?: string,
    public tags?: string[]
  ) {
    super(title, vscode.TreeItemCollapsibleState.None);

    this.tooltip = this.buildTooltip();
    this.description = this.buildDescription();
    this.contextValue = "todo";
    this.iconPath = this.getIcon();

    // Add command to toggle on click
    this.command = {
      command: "taskman.toggle",
      title: "Toggle Task",
      arguments: [this],
    };
  }

  private buildTooltip(): string {
    let tooltip = `${this.title}${this.completed ? " ✓" : ""}`;

    if (this.description) {
      tooltip += `\n\nDescription: ${this.description}`;
    }

    if (this.dueDate) {
      const date = new Date(this.dueDate);
      tooltip += `\nDue: ${date.toLocaleDateString()}`;
    }

    if (this.tags && this.tags.length > 0) {
      tooltip += `\nTags: ${this.tags.join(", ")}`;
    }

    tooltip += `\nGroup: ${this.group}`;

    return tooltip;
  }

  private buildDescription(): string {
    const parts: string[] = [];

    if (this.dueDate) {
      const date = new Date(this.dueDate);
      const now = new Date();
      const isOverdue = date < now && !this.completed;
      const isToday = date.toDateString() === now.toDateString();

      if (isOverdue) {
        parts.push("🔴 Overdue");
      } else if (isToday) {
        parts.push("🟡 Due today");
      }
    }

    if (this.tags && this.tags.length > 0) {
      parts.push(`#${this.tags.join(" #")}`);
    }

    return parts.join(" ");
  }

  private getIcon(): vscode.ThemeIcon {
    if (this.completed) {
      return new vscode.ThemeIcon(
        "check",
        new vscode.ThemeColor("charts.green")
      );
    }

    if (this.dueDate) {
      const date = new Date(this.dueDate);
      const now = new Date();
      const isOverdue = date < now;
      const isToday = date.toDateString() === now.toDateString();

      if (isOverdue) {
        return new vscode.ThemeIcon(
          "alert",
          new vscode.ThemeColor("errorForeground")
        );
      } else if (isToday) {
        return new vscode.ThemeIcon(
          "clock",
          new vscode.ThemeColor("charts.yellow")
        );
      }
    }

    return new vscode.ThemeIcon("circle-outline");
  }

  // Create a plain object for storage
  toStorageObject(): TodoStorageObject {
    return {
      id: this.id,
      title: this.title,
      completed: this.completed,
      group: this.group,
      description: this.description,
      dueDate: this.dueDate,
      tags: this.tags,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  }

  // Create TodoItem from storage object
  static fromStorageObject(obj: TodoStorageObject): TodoItem {
    return new TodoItem(
      obj.id,
      obj.title,
      obj.completed,
      obj.group,
      obj.description,
      obj.dueDate,
      obj.tags
    );
  }
}

export class TodoGroup extends vscode.TreeItem {
  constructor(
    public readonly name: string,
    public readonly todos: TodoItem[] = []
  ) {
    super(name, vscode.TreeItemCollapsibleState.Expanded);

    this.tooltip = this.buildTooltip();
    this.description = this.buildDescription();
    this.contextValue = "group";
    this.iconPath = new vscode.ThemeIcon("folder");
  }

  private buildTooltip(): string {
    const total = this.todos.length;
    const completed = this.todos.filter((t) => t.completed).length;
    const pending = total - completed;

    return `${this.name}\nTotal: ${total} | Completed: ${completed} | Pending: ${pending}`;
  }

  private buildDescription(): string {
    const total = this.todos.length;
    const completed = this.todos.filter((t) => t.completed).length;
    const pending = total - completed;

    if (total === 0) {
      return "Empty";
    }

    return `${pending}/${total}`;
  }

  // Create a plain object for storage
  toStorageObject(): TodoGroupStorageObject {
    return {
      name: this.name,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  }

  // Create TodoGroup from storage object
  static fromStorageObject(
    obj: TodoGroupStorageObject,
    todos: TodoItem[] = []
  ): TodoGroup {
    return new TodoGroup(obj.name, todos);
  }
}

// Storage interfaces
export interface TodoStorageObject {
  id: string;
  title: string;
  completed: boolean;
  group: string;
  description?: string;
  dueDate?: string;
  tags?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface TodoGroupStorageObject {
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface TodoStorageData {
  version: number;
  todos: TodoStorageObject[];
  groups: TodoGroupStorageObject[];
}

// Schema migration helper
export class SchemaMigration {
  static migrate(data: any): TodoStorageData {
    // Handle version 1 (initial version)
    if (!data.version || data.version === 1) {
      return {
        version: 1,
        todos: data.todos || [],
        groups: data.groups || [],
      };
    }

    // Future version migrations would go here
    return data;
  }
}

// ============================================================================
// Action List Models (from TaskMan-v2 PostgreSQL)
// ============================================================================

/**
 * Action list status enum matching PostgreSQL schema
 * 9 statuses: planned, new, pending, active, in_progress, blocked, completed, archived, cancelled
 */
export type ActionListStatus =
  | "planned"
  | "new"
  | "pending"
  | "active"
  | "in_progress"
  | "blocked"
  | "completed"
  | "archived"
  | "cancelled";

/**
 * Action list priority enum
 */
export type ActionListPriority = "low" | "medium" | "high" | "critical";

/**
 * Action list item (checklist item within an action list)
 */
export interface ActionListItem {
  id: string;
  text: string;
  completed: boolean;
  created_at?: string;
  completed_at?: string;
}

/**
 * Evidence reference
 */
export interface EvidenceRef {
  id: string;
  type: string;
  path?: string;
  metadata?: Record<string, any>;
}

/**
 * Deletion metadata for soft delete tracking
 */
export interface DeletionMetadata {
  deleted_at: string;
  deleted_by?: string;
  deletion_note?: string;
}

/**
 * Action list data model matching PostgreSQL schema
 * Schema from taskman_v2.action_lists (20 columns)
 */
export interface ActionList {
  id: string; // character varying NOT NULL
  title: string; // character varying NOT NULL
  description?: string; // text NULL
  status: ActionListStatus; // character varying NOT NULL
  owner?: string; // character varying NULL
  tags?: Record<string, any>; // json NULL
  project_id?: string; // character varying NULL
  sprint_id?: string; // character varying NULL
  items: ActionListItem[]; // json NOT NULL
  geometry_shape?: string; // character varying NULL
  priority?: ActionListPriority; // character varying NULL
  due_date?: string; // timestamp with time zone NULL
  evidence_refs?: EvidenceRef[]; // json NULL
  extra_metadata?: Record<string, any>; // json NULL
  notes?: string; // text NULL
  parent_deleted_at?: string; // timestamp with time zone NULL
  parent_deletion_note?: Record<string, any>; // json NULL
  created_at?: string; // timestamp with time zone NULL DEFAULT now()
  updated_at?: string; // timestamp with time zone NULL DEFAULT now()
  completed_at?: string; // timestamp with time zone NULL
}

/**
 * Action list tree item for VSCode TreeView
 */
export class ActionListTreeItem extends vscode.TreeItem {
  constructor(
    public readonly actionList: ActionList
  ) {
    super(
      actionList.title,
      vscode.TreeItemCollapsibleState.Collapsed
    );

    this.tooltip = this.buildTooltip();
    this.description = this.buildDescription();
    this.contextValue = "actionList";
    this.iconPath = this.getIcon();

    // Add command to view details on click
    this.command = {
      command: "taskman.viewActionList",
      title: "View Action List",
      arguments: [this],
    };
  }

  private buildTooltip(): string {
    const al = this.actionList;
    let tooltip = `${al.title}\nStatus: ${al.status}`;

    if (al.description) {
      tooltip += `\n\nDescription: ${al.description}`;
    }

    const totalItems = al.items.length;
    const completedItems = al.items.filter((i) => i.completed).length;
    tooltip += `\n\nItems: ${completedItems}/${totalItems} completed`;

    if (al.priority) {
      tooltip += `\nPriority: ${al.priority}`;
    }

    if (al.due_date) {
      const date = new Date(al.due_date);
      tooltip += `\nDue: ${date.toLocaleDateString()}`;
    }

    if (al.owner) {
      tooltip += `\nOwner: ${al.owner}`;
    }

    if (al.project_id) {
      tooltip += `\nProject: ${al.project_id}`;
    }

    if (al.sprint_id) {
      tooltip += `\nSprint: ${al.sprint_id}`;
    }

    return tooltip;
  }

  private buildDescription(): string {
    const al = this.actionList;
    const parts: string[] = [];

    // Items count
    const totalItems = al.items.length;
    const completedItems = al.items.filter((i) => i.completed).length;
    parts.push(`${completedItems}/${totalItems}`);

    // Due date indicator
    if (al.due_date) {
      const date = new Date(al.due_date);
      const now = new Date();
      const isOverdue = date < now && al.status !== "completed";
      const isToday = date.toDateString() === now.toDateString();

      if (isOverdue) {
        parts.push("🔴 Overdue");
      } else if (isToday) {
        parts.push("🟡 Due today");
      }
    }

    return parts.join(" ");
  }

  private getIcon(): vscode.ThemeIcon {
    const al = this.actionList;

    // Status-based icons
    switch (al.status) {
      case "completed":
        return new vscode.ThemeIcon(
          "check-all",
          new vscode.ThemeColor("charts.green")
        );
      case "archived":
        return new vscode.ThemeIcon("archive");
      case "cancelled":
        return new vscode.ThemeIcon(
          "close",
          new vscode.ThemeColor("errorForeground")
        );
      case "blocked":
        return new vscode.ThemeIcon(
          "error",
          new vscode.ThemeColor("charts.red")
        );
      case "in_progress":
      case "active":
        return new vscode.ThemeIcon(
          "sync",
          new vscode.ThemeColor("charts.blue")
        );
      case "pending":
        return new vscode.ThemeIcon("clock");
      case "new":
        return new vscode.ThemeIcon(
          "sparkle",
          new vscode.ThemeColor("charts.yellow")
        );
      case "planned":
        return new vscode.ThemeIcon("calendar");
      default:
        return new vscode.ThemeIcon("checklist");
    }
  }
}

/**
 * Action list item tree item for VSCode TreeView
 */
export class ActionListItemTreeItem extends vscode.TreeItem {
  constructor(
    public readonly item: ActionListItem,
    public readonly parentActionList: ActionList
  ) {
    super(item.text, vscode.TreeItemCollapsibleState.None);

    this.tooltip = this.buildTooltip();
    this.contextValue = "actionListItem";
    this.iconPath = this.getIcon();

    // Add command to toggle on click
    this.command = {
      command: "taskman.toggleActionListItem",
      title: "Toggle Action List Item",
      arguments: [this],
    };
  }

  private buildTooltip(): string {
    let tooltip = `${this.item.text}${this.item.completed ? " ✓" : ""}`;

    if (this.item.created_at) {
      const date = new Date(this.item.created_at);
      tooltip += `\nCreated: ${date.toLocaleDateString()}`;
    }

    if (this.item.completed && this.item.completed_at) {
      const date = new Date(this.item.completed_at);
      tooltip += `\nCompleted: ${date.toLocaleDateString()}`;
    }

    tooltip += `\n\nParent: ${this.parentActionList.title}`;

    return tooltip;
  }

  private getIcon(): vscode.ThemeIcon {
    if (this.item.completed) {
      return new vscode.ThemeIcon(
        "check",
        new vscode.ThemeColor("charts.green")
      );
    }

    return new vscode.ThemeIcon("circle-outline");
  }
}
