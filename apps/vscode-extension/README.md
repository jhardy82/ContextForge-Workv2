# VS Code Todos Extension

A production-ready Todo List extension for Visual Studio Code with TreeView sidebar, persistent storage, and comprehensive task management features.

## Features

### 🌳 TreeView Sidebar
- **Organized Todo Groups**: Todos are organized into customizable groups (Today, Upcoming, Completed, etc.)
- **Visual Status Indicators**: Different icons for completed, pending, overdue, and due-today todos
- **Collapsible Groups**: Expand/collapse groups to focus on what matters
- **Context Menus**: Right-click on todos and groups for quick actions

### 💾 Persistent Storage
- **VS Code Memento Integration**: Uses VS Code's built-in storage system
- **Global vs Workspace Storage**: Choose between storing todos globally or per workspace
- **Schema Migration**: Automatic migration system for future data structure changes
- **Import/Export**: Export todos to JSON and import from backups

### ⚡ Commands & Keybindings
- **Add Todo**: `Ctrl+Shift+T` (Cmd+Shift+T on Mac)
- **Toggle Complete**: `Ctrl+Enter` (Cmd+Enter on Mac)
- **Delete Todo**: `Ctrl+Backspace` (Cmd+Backspace on Mac)
- **Refresh View**: Manual refresh button in tree view
- **Move Todo**: Move todos between groups
- **Edit Todo**: Inline editing and detailed webview editing

### 🎨 Webview Details Panel
- **Rich Todo Editor**: Edit title, description, due date, and tags
- **Visual Status Toggle**: Click to toggle completion status
- **Due Date Management**: Set and track due dates with visual indicators
- **Tag System**: Organize todos with custom tags
- **Metadata Display**: View creation and modification times

### 🔧 Configuration Options
- **Storage Mode**: Global or workspace-specific todo storage
- **Default Groups**: Customize the initial group structure
- **Group Ordering**: Set the display order of groups
- **Webview Toggle**: Show/hide the details panel
- **Sort Options**: Sort todos by creation date, due date, completion status, or title

## Installation

### From Source
1. Clone this repository
2. Navigate to the `vscode-extension` directory
3. Run `npm install` to install dependencies
4. Run `npm run compile` to build the extension
5. Press `F5` to open a new Extension Development Host window

### From Package
1. Run `npm run package` to create a VSIX file
2. Install using `code --install-extension vscode-todos-1.0.0.vsix`

## Usage

### Getting Started
1. Open VS Code with a workspace folder
2. The "Todos" view will appear in the Explorer panel
3. Click the "+" icon to add your first todo
4. Use the context menu (right-click) for more actions

### Adding Todos
- Click the "+" icon in the tree view title
- Use the command palette: `Ctrl+Shift+P` → "Add Todo"
- Use the keyboard shortcut: `Ctrl+Shift+T`

### Managing Groups
- Click the folder icon to add new groups
- Drag and drop todos between groups (coming soon)
- Right-click groups for group-specific actions

### Using the Details Panel
- Click on any todo to see its details in the bottom panel
- Edit all todo properties in the rich editor
- Toggle completion status with one click
- Delete todos with confirmation

## Configuration

Access settings via `File > Preferences > Settings` and search for "todos":

```json
{
  "todos.storageMode": "workspace",
  "todos.defaultGroups": ["Today", "Upcoming", "Completed"],
  "todos.showWebviewDetails": true,
  "todos.groupOrdering": ["Today", "Upcoming", "Completed"],
  "todos.sortBy": "created",
  "todos.sortOrder": "asc",
  "todos.hideEmptyGroups": false
}
```

## Development

### Setup
```bash
cd vscode-extension
npm install
npm run compile
```

### Testing
```bash
npm run test        # Run unit tests
npm run lint        # Run ESLint
npm run watch       # Watch for changes
```

### Building
```bash
npm run compile     # Compile TypeScript
npm run package     # Create VSIX package
npm run publish     # Publish to marketplace
```

## Architecture

### Core Components
- **Extension.ts**: Main activation and command registration
- **TodoTreeDataProvider**: TreeView data provider implementation
- **StorageManager**: Persistent storage abstraction
- **TodoWebviewProvider**: Webview details panel provider
- **Models**: Data models with storage serialization

### Data Flow
1. User interacts with TreeView or Webview
2. Commands trigger actions in extension.ts
3. StorageManager handles persistence
4. TreeDataProvider updates the view
5. WebviewProvider updates details panel

### Storage Schema
```typescript
interface TodoStorageData {
  version: number;
  todos: TodoStorageObject[];
  groups: TodoGroupStorageObject[];
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Testing

The extension includes comprehensive unit tests covering:
- Model creation and serialization
- Storage operations
- Tree data provider functionality
- Schema migration
- UI state management

Run tests with `npm test` or use VS Code's integrated test runner.

## Roadmap

- [ ] Drag and drop todo reordering
- [ ] Todo priority levels
- [ ] Recurring todo support
- [ ] Todo templates
- [ ] Search and filtering
- [ ] Statistics dashboard
- [ ] Integration with external task systems
- [ ] Collaborative todos
- [ ] Mobile companion app

## License

MIT License - see LICENSE file for details.

## Support

For issues, feature requests, or questions:
- GitHub Issues: [Create an issue](https://github.com/spark-template/vscode-todos/issues)
- VS Code Marketplace: Rate and review
- Documentation: Check this README and inline code comments