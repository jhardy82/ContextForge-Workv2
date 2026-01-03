# Change Log

All notable changes to the "VS Code Todos" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of VS Code Todos extension
- TreeView sidebar integration with customizable groups
- Persistent storage using VS Code Memento API
- Webview details panel for rich todo editing
- Context menu actions for todos and groups
- Keyboard shortcuts for common actions
- Configuration options for storage mode and UI preferences
- Schema migration system for future updates
- Import/export functionality for todo data
- Comprehensive test suite with unit tests
- ESLint configuration and code quality checks

### Features
- **Todo Management**
  - Create, edit, delete, and toggle todos
  - Organize todos into customizable groups
  - Set due dates with visual indicators for overdue items
  - Add descriptions and tags to todos
  - Move todos between groups

- **User Interface**
  - TreeView integration in Explorer panel
  - Webview details panel with rich editing
  - Context menus for quick actions
  - Visual status indicators (completed, overdue, due today)
  - Collapsible groups with todo counts

- **Storage & Persistence**
  - Global or workspace-specific storage options
  - Automatic schema migration
  - JSON import/export functionality
  - Data integrity validation

- **Configuration**
  - Customizable default groups
  - Configurable group ordering
  - Flexible sorting options
  - Toggle webview visibility
  - Hide empty groups option

- **Developer Experience**
  - TypeScript implementation
  - Comprehensive test coverage
  - ESLint code quality
  - VS Code debugging configuration
  - Documentation and examples

### Commands
- `todos.add` - Add new todo (Ctrl+Shift+T)
- `todos.edit` - Edit existing todo
- `todos.toggle` - Toggle completion status (Ctrl+Enter)
- `todos.delete` - Delete todo or group (Ctrl+Backspace)
- `todos.move` - Move todo between groups
- `todos.openDetails` - Open details in webview
- `todos.refresh` - Refresh tree view
- `todos.addGroup` - Add new group

### Configuration Options
- `todos.storageMode` - Global or workspace storage
- `todos.defaultGroups` - Initial group structure
- `todos.showWebviewDetails` - Show/hide details panel
- `todos.groupOrdering` - Custom group order
- `todos.sortBy` - Todo sorting criteria
- `todos.sortOrder` - Ascending or descending sort
- `todos.hideEmptyGroups` - Hide groups with no todos

## [Unreleased]

### Planned Features
- Drag and drop todo reordering
- Priority levels for todos
- Recurring todo support
- Todo templates
- Advanced search and filtering
- Statistics dashboard
- External system integrations