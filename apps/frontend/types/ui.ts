/**
 * UI State Types for Progressive Disclosure and Field Visibility
 */

// ============================================================================
// Field Visibility (Progressive Disclosure)
// ============================================================================

export interface FieldVisibility {
  // Tier 2 sections (collapsible, default closed)
  showRelationships: boolean;
  showTimeEffort: boolean;
  showPeople: boolean;
  showStatusDetails: boolean;

  // Tier 3 master toggle
  showAdvanced: boolean;

  // Tier 3 sections (only relevant when showAdvanced=true)
  showBusinessContext: boolean;
  showTechnical: boolean;
  showQuality: boolean;
  showCOFDimensions: boolean;
}

export const DEFAULT_FIELD_VISIBILITY: FieldVisibility = {
  showRelationships: false,
  showTimeEffort: false,
  showPeople: false,
  showStatusDetails: false,
  showAdvanced: false,
  showBusinessContext: false,
  showTechnical: false,
  showQuality: false,
  showCOFDimensions: false,
};

// ============================================================================
// View Modes
// ============================================================================

export type ViewMode = "tree" | "kanban" | "list" | "timeline" | "sprint";

export type SidebarState = "expanded" | "collapsed" | "hidden";

// ============================================================================
// UI Store State
// ============================================================================

export interface UIState {
  /** Currently selected node ID */
  selectedId: string | null;
  /** Currently focused node ID (for keyboard nav) */
  focusedId: string | null;
  /** Set of expanded node IDs */
  expandedIds: Set<string>;
  /** Field visibility preferences */
  fieldVisibility: FieldVisibility;
  /** Current view mode */
  viewMode: ViewMode;
  /** Sidebar state */
  sidebarState: SidebarState;
  /** Detail panel open */
  detailPanelOpen: boolean;
}

export const DEFAULT_UI_STATE: Omit<UIState, "expandedIds"> & {
  expandedIds: string[];
} = {
  selectedId: null,
  focusedId: null,
  expandedIds: [],
  fieldVisibility: DEFAULT_FIELD_VISIBILITY,
  viewMode: "tree",
  sidebarState: "expanded",
  detailPanelOpen: false,
};

// ============================================================================
// Notification Types
// ============================================================================

export type NotificationType = "success" | "error" | "warning" | "info";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
}

// ============================================================================
// Dialog State
// ============================================================================

export interface DialogState {
  /** Create task dialog */
  createTask: boolean;
  /** Create project dialog */
  createProject: boolean;
  /** Settings dialog */
  settings: boolean;
  /** Delete confirmation */
  deleteConfirm: boolean;
  /** Command palette */
  commandPalette: boolean;
}

export const DEFAULT_DIALOG_STATE: DialogState = {
  createTask: false,
  createProject: false,
  settings: false,
  deleteConfirm: false,
  commandPalette: false,
};

// ============================================================================
// Status Colors (WCAG AA Compliant)
// ============================================================================

import type { TaskPriorityValue, TaskStatusValue } from "./objects";

export const STATUS_BADGE_STYLES: Record<
  TaskStatusValue,
  { bg: string; text: string; border: string }
> = {
  new: { bg: "bg-gray-100", text: "text-gray-700", border: "border-gray-300" },
  pending: {
    bg: "bg-yellow-100",
    text: "text-yellow-700",
    border: "border-yellow-300",
  },
  in_progress: {
    bg: "bg-blue-100",
    text: "text-blue-700",
    border: "border-blue-300",
  },
  done: {
    bg: "bg-green-100",
    text: "text-green-700",
    border: "border-green-300",
  },
  blocked: {
    bg: "bg-purple-100",
    text: "text-purple-700",
    border: "border-purple-300",
  },
  cancelled: {
    bg: "bg-gray-100",
    text: "text-gray-500",
    border: "border-gray-300",
  },
};

export const PRIORITY_BADGE_STYLES: Record<
  TaskPriorityValue,
  { bg: string; text: string; border: string }
> = {
  low: { bg: "bg-gray-100", text: "text-gray-600", border: "border-gray-300" },
  medium: {
    bg: "bg-yellow-100",
    text: "text-yellow-800",
    border: "border-yellow-400",
  },
  high: {
    bg: "bg-orange-100",
    text: "text-orange-800",
    border: "border-orange-400",
  },
  critical: {
    bg: "bg-red-100",
    text: "text-red-800",
    border: "border-red-400",
  },
};

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  description: string;
  action: string;
}

export const KEYBOARD_SHORTCUTS: KeyboardShortcut[] = [
  {
    key: "k",
    ctrl: true,
    description: "Open command palette",
    action: "openCommandPalette",
  },
  {
    key: "n",
    ctrl: true,
    description: "Create new task",
    action: "createTask",
  },
  {
    key: "e",
    ctrl: true,
    description: "Edit selected task",
    action: "editTask",
  },
  { key: "Delete", description: "Delete selected task", action: "deleteTask" },
  { key: "/", description: "Focus search", action: "focusSearch" },
  { key: "Escape", description: "Close dialog/deselect", action: "escape" },
  { key: "z", ctrl: true, description: "Undo", action: "undo" },
  { key: "z", ctrl: true, shift: true, description: "Redo", action: "redo" },
];
