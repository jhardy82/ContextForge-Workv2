import * as vscode from "vscode";
import { DatabaseService } from "./databaseService";
import {
  ActionList,
  ActionListItemTreeItem,
  ActionListStatus,
  ActionListTreeItem,
} from "./models";

/**
 * Tree data provider for action lists from TaskMan-v2 PostgreSQL database
 * Displays action lists and their checklist items in the VS Code TreeView
 */
export class ActionListProvider
  implements vscode.TreeDataProvider<vscode.TreeItem>
{
  private _onDidChangeTreeData: vscode.EventEmitter<
    vscode.TreeItem | undefined | null | void
  > = new vscode.EventEmitter<vscode.TreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<
    vscode.TreeItem | undefined | null | void
  > = this._onDidChangeTreeData.event;

  private actionLists: ActionList[] = [];

  constructor(private databaseService: DatabaseService) {
    // Constructor - will load data via refresh()
  }

  /**
   * Refresh the tree view
   */
  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  /**
   * Get tree item for display
   */
  getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
    return element;
  }

  /**
   * Get children for tree expansion
   * - null/undefined = root level (show all action lists)
   * - ActionListTreeItem = show action list items
   * - ActionListItemTreeItem = leaf node (no children)
   */
  async getChildren(
    element?: vscode.TreeItem
  ): Promise<vscode.TreeItem[] | undefined> {
    if (!element) {
      // Root level: return all action lists
      return this.getRootActionLists();
    }

    if (element instanceof ActionListTreeItem) {
      // Action list expanded: return its items
      return this.getActionListItems(element);
    }

    // Leaf nodes (ActionListItemTreeItem) have no children
    return undefined;
  }

  /**
   * Get root-level action lists
   * Groups action lists by status for better organization
   */
  private async getRootActionLists(): Promise<vscode.TreeItem[]> {
    try {
      // Load action lists from database
      await this.loadActionLists();

      if (this.actionLists.length === 0) {
        // No action lists found
        const emptyItem = new vscode.TreeItem(
          "No action lists found",
          vscode.TreeItemCollapsibleState.None
        );
        emptyItem.iconPath = new vscode.ThemeIcon("info");
        emptyItem.contextValue = "empty";
        return [emptyItem];
      }

      // Group by status
      const statusGroups = this.groupByStatus(this.actionLists);

      // Create tree items for each status group
      const treeItems: vscode.TreeItem[] = [];

      // Status display order
      const statusOrder: ActionListStatus[] = [
        "in_progress",
        "active",
        "pending",
        "new",
        "planned",
        "blocked",
        "completed",
        "archived",
        "cancelled",
      ];

      for (const status of statusOrder) {
        const actionLists = statusGroups.get(status);
        if (actionLists && actionLists.length > 0) {
          // Create a group node for this status
          const groupItem = new vscode.TreeItem(
            this.formatStatusLabel(status, actionLists.length),
            vscode.TreeItemCollapsibleState.Expanded
          );
          groupItem.iconPath = this.getStatusIcon(status);
          groupItem.contextValue = `actionListStatusGroup:${status}`;

          // Add action lists as children
          const children = actionLists.map((al) => new ActionListTreeItem(al));

          // Store children for later retrieval
          (groupItem as any)._children = children;

          treeItems.push(groupItem);
        }
      }

      return treeItems;
    } catch (error) {
      console.error("Error loading action lists:", error);

      const errorItem = new vscode.TreeItem(
        "Error loading action lists",
        vscode.TreeItemCollapsibleState.None
      );
      errorItem.iconPath = new vscode.ThemeIcon("error");
      errorItem.tooltip =
        error instanceof Error ? error.message : String(error);
      return [errorItem];
    }
  }

  /**
   * Get items for an action list
   */
  private getActionListItems(element: ActionListTreeItem): vscode.TreeItem[] {
    const al = element.actionList;

    if (al.items.length === 0) {
      const emptyItem = new vscode.TreeItem(
        "No items",
        vscode.TreeItemCollapsibleState.None
      );
      emptyItem.iconPath = new vscode.ThemeIcon("dash");
      emptyItem.contextValue = "empty";
      return [emptyItem];
    }

    return al.items.map((item) => new ActionListItemTreeItem(item, al));
  }

  /**
   * Group action lists by status
   */
  private groupByStatus(
    actionLists: ActionList[]
  ): Map<ActionListStatus, ActionList[]> {
    const groups = new Map<ActionListStatus, ActionList[]>();

    for (const al of actionLists) {
      const status = al.status;
      if (!groups.has(status)) {
        groups.set(status, []);
      }
      groups.get(status)!.push(al);
    }

    return groups;
  }

  /**
   * Format status label for group node
   */
  private formatStatusLabel(status: ActionListStatus, count: number): string {
    const statusLabels: Record<ActionListStatus, string> = {
      in_progress: "In Progress",
      active: "Active",
      pending: "Pending",
      new: "New",
      planned: "Planned",
      blocked: "Blocked",
      completed: "Completed",
      archived: "Archived",
      cancelled: "Cancelled",
    };

    return `${statusLabels[status]} (${count})`;
  }

  /**
   * Get icon for status group
   */
  private getStatusIcon(status: ActionListStatus): vscode.ThemeIcon {
    switch (status) {
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
      case "blocked":
        return new vscode.ThemeIcon(
          "error",
          new vscode.ThemeColor("charts.red")
        );
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
      default:
        return new vscode.ThemeIcon("checklist");
    }
  }

  /**
   * Load action lists from database via DTM API
   */
  private async loadActionLists(): Promise<void> {
    try {
      this.actionLists = await this.databaseService.loadActionLists();
    } catch (error) {
      console.error("Error loading action lists:", error);
      this.actionLists = [];
      throw error; // Re-throw to be handled by caller
    }
  }

  /**
   * Get all action lists (for external access)
   */
  getActionLists(): ActionList[] {
    return this.actionLists;
  }

  /**
   * Find action list by ID
   */
  findActionListById(id: string): ActionList | undefined {
    return this.actionLists.find((al) => al.id === id);
  }

  /**
   * Toggle action list item completion
   */
  async toggleActionListItem(
    actionListId: string,
    itemId: string
  ): Promise<void> {
    const actionList = this.findActionListById(actionListId);
    if (!actionList) {
      throw new Error(`Action list ${actionListId} not found`);
    }

    const item = actionList.items.find((i) => i.id === itemId);
    if (!item) {
      throw new Error(
        `Item ${itemId} not found in action list ${actionListId}`
      );
    }

    // Toggle completion
    item.completed = !item.completed;
    item.completed_at = item.completed ? new Date().toISOString() : undefined;

    // Persist change to database via DTM API
    await this.databaseService.toggleActionListItem(
      actionListId,
      itemId,
      item.completed
    );

    // Refresh tree view
    this.refresh();
  }

  /**
   * Create new action list
   */
  async createActionList(actionList: Partial<ActionList>): Promise<void> {
    // Create via DTM API
    await this.databaseService.createActionList(actionList);

    // Refresh tree view
    this.refresh();
  }

  /**
   * Delete action list
   */
  async deleteActionList(id: string): Promise<void> {
    // Delete via DTM API
    await this.databaseService.deleteActionList(id);

    // Refresh tree view
    this.refresh();
  }
}
