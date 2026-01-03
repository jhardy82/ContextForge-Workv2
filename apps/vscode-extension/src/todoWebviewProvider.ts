import * as vscode from 'vscode';
import { TodoItem } from './models';
import { StorageManager } from './storageManager';

export class TodoWebviewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "todos.details";

  private _view?: vscode.WebviewView;
  private _currentTodo?: TodoItem;

  constructor(
    private readonly context: vscode.ExtensionContext,
    private readonly storageManager: StorageManager
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      // Allow scripts in the webview
      enableScripts: true,
      localResourceRoots: [this.context.extensionUri],
    };

    webviewView.webview.html = this.getInitialHtml();

    // Handle messages from the webview
    webviewView.webview.onDidReceiveMessage(
      async (message) => {
        switch (message.command) {
          case "updateTodo":
            await this.handleUpdateTodo(message.data);
            break;
          case "deleteTodo":
            await this.handleDeleteTodo(message.todoId);
            break;
          case "toggleComplete":
            await this.handleToggleComplete(message.todoId);
            break;
        }
      },
      undefined,
      this.context.subscriptions
    );
  }

  public async showTodoDetails(todo: TodoItem) {
    this._currentTodo = todo;

    if (this._view) {
      this._view.webview.html = this.getTodoDetailsHtml(todo);
      this._view.show?.(true); // `show` is not available in all versions
    }
  }

  private async handleUpdateTodo(data: any) {
    if (!this._currentTodo) {
      return;
    }

    // Update the todo with new data
    this._currentTodo.title = data.title;
    this._currentTodo.description = data.description;
    this._currentTodo.dueDate = data.dueDate;
    this._currentTodo.tags = data.tags
      ? data.tags
          .split(",")
          .map((tag: string) => tag.trim())
          .filter((tag: string) => tag)
      : undefined;

    await this.storageManager.updateTodo(this._currentTodo);

    // Refresh the tree view
    vscode.commands.executeCommand("todos.refresh");

    vscode.window.showInformationMessage("Todo updated successfully");
  }

  private async handleDeleteTodo(todoId: string) {
    if (!this._currentTodo || this._currentTodo.id !== todoId) {
      return;
    }

    const result = await vscode.window.showWarningMessage(
      `Are you sure you want to delete "${this._currentTodo.title}"?`,
      { modal: true },
      "Delete"
    );

    if (result === "Delete") {
      await this.storageManager.deleteTodo(todoId);
      this._currentTodo = undefined;

      if (this._view) {
        this._view.webview.html = this.getInitialHtml();
      }

      // Refresh the tree view
      vscode.commands.executeCommand("todos.refresh");

      vscode.window.showInformationMessage("Todo deleted successfully");
    }
  }

  private async handleToggleComplete(todoId: string) {
    if (!this._currentTodo || this._currentTodo.id !== todoId) {
      return;
    }

    this._currentTodo.completed = !this._currentTodo.completed;
    await this.storageManager.updateTodo(this._currentTodo);

    // Update the webview
    if (this._view) {
      this._view.webview.html = this.getTodoDetailsHtml(this._currentTodo);
    }

    // Refresh the tree view
    vscode.commands.executeCommand("todos.refresh");

    const status = this._currentTodo.completed ? "completed" : "pending";
    vscode.window.showInformationMessage(`Todo marked as ${status}`);
  }

  private getInitialHtml(): string {
    return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Todo Details</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 16px;
                    margin: 0;
                }
                .empty-state {
                    text-align: center;
                    padding: 32px 16px;
                    color: var(--vscode-descriptionForeground);
                }
                .empty-state h3 {
                    margin: 0 0 8px 0;
                    font-weight: normal;
                }
                .empty-state p {
                    margin: 0;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <div class="empty-state">
                <h3>No Todo Selected</h3>
                <p>Select a todo from the tree view to see its details and edit it here.</p>
            </div>
        </body>
        </html>`;
  }

  private getTodoDetailsHtml(todo: TodoItem): string {
    const dueDate = todo.dueDate
      ? new Date(todo.dueDate).toISOString().split("T")[0]
      : "";
    const tags = todo.tags ? todo.tags.join(", ") : "";

    return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Todo Details</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 16px;
                    margin: 0;
                }

                .todo-header {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 16px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }

                .todo-status {
                    font-size: 18px;
                    cursor: pointer;
                    user-select: none;
                }

                .todo-title {
                    font-size: 1.1em;
                    font-weight: 600;
                    margin: 0;
                    flex: 1;
                }

                .completed {
                    text-decoration: line-through;
                    opacity: 0.7;
                }

                .form-group {
                    margin-bottom: 16px;
                }

                .form-group label {
                    display: block;
                    margin-bottom: 4px;
                    font-weight: 500;
                    color: var(--vscode-input-foreground);
                }

                .form-group input,
                .form-group textarea {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid var(--vscode-input-border);
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border-radius: 2px;
                    font-family: inherit;
                    font-size: inherit;
                    box-sizing: border-box;
                }

                .form-group textarea {
                    resize: vertical;
                    min-height: 80px;
                }

                .form-group input:focus,
                .form-group textarea:focus {
                    outline: 1px solid var(--vscode-focusBorder);
                    border-color: var(--vscode-focusBorder);
                }

                .button-group {
                    display: flex;
                    gap: 8px;
                    margin-top: 20px;
                }

                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 2px;
                    cursor: pointer;
                    font-family: inherit;
                    font-size: inherit;
                    font-weight: 500;
                }

                .btn-primary {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                }

                .btn-primary:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }

                .btn-secondary {
                    background-color: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }

                .btn-secondary:hover {
                    background-color: var(--vscode-button-secondaryHoverBackground);
                }

                .btn-danger {
                    background-color: var(--vscode-errorForeground);
                    color: var(--vscode-editor-background);
                }

                .btn-danger:hover {
                    opacity: 0.9;
                }

                .metadata {
                    margin-top: 20px;
                    padding-top: 16px;
                    border-top: 1px solid var(--vscode-panel-border);
                    font-size: 0.9em;
                    color: var(--vscode-descriptionForeground);
                }

                .metadata-item {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 4px;
                }
            </style>
        </head>
        <body>
            <div class="todo-header">
                <span class="todo-status" onclick="toggleComplete()" title="Click to toggle completion">
                    ${todo.completed ? "✅" : "⭕"}
                </span>
                <h2 class="todo-title ${
                  todo.completed ? "completed" : ""
                }">${this.escapeHtml(todo.title)}</h2>
            </div>

            <form id="todoForm">
                <div class="form-group">
                    <label for="title">Title</label>
                    <input type="text" id="title" name="title" value="${this.escapeHtml(
                      todo.title
                    )}" required>
                </div>

                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" placeholder="Optional description...">${this.escapeHtml(
                      todo.description || ""
                    )}</textarea>
                </div>

                <div class="form-group">
                    <label for="dueDate">Due Date</label>
                    <input type="date" id="dueDate" name="dueDate" value="${dueDate}">
                </div>

                <div class="form-group">
                    <label for="tags">Tags</label>
                    <input type="text" id="tags" name="tags" value="${this.escapeHtml(
                      tags
                    )}" placeholder="Comma-separated tags...">
                </div>

                <div class="button-group">
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                    <button type="button" class="btn btn-secondary" onclick="toggleComplete()">
                        ${todo.completed ? "Mark Pending" : "Mark Complete"}
                    </button>
                    <button type="button" class="btn btn-danger" onclick="deleteTodo()">Delete</button>
                </div>
            </form>

            <div class="metadata">
                <div class="metadata-item">
                    <span>Group:</span>
                    <span>${this.escapeHtml(todo.group)}</span>
                </div>
                <div class="metadata-item">
                    <span>Status:</span>
                    <span>${todo.completed ? "Completed" : "Pending"}</span>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                document.getElementById('todoForm').addEventListener('submit', (e) => {
                    e.preventDefault();

                    const formData = new FormData(e.target);
                    const data = {
                        title: formData.get('title'),
                        description: formData.get('description'),
                        dueDate: formData.get('dueDate'),
                        tags: formData.get('tags')
                    };

                    vscode.postMessage({
                        command: 'updateTodo',
                        data: data
                    });
                });

                function toggleComplete() {
                    vscode.postMessage({
                        command: 'toggleComplete',
                        todoId: '${todo.id}'
                    });
                }

                function deleteTodo() {
                    vscode.postMessage({
                        command: 'deleteTodo',
                        todoId: '${todo.id}'
                    });
                }
            </script>
        </body>
        </html>`;
  }

  private escapeHtml(unsafe: string): string {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}
