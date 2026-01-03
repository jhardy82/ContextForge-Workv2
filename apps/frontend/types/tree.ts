/**
 * Tree-specific types for hierarchical navigation
 */

import type { HierarchyLevel, TreeNode } from './objects';

// ============================================================================
// Tree State Types
// ============================================================================

export interface TreeNodeState {
  /** Whether this node is expanded */
  expanded: boolean;
  /** Whether this node is selected */
  selected: boolean;
  /** Whether this node has keyboard focus */
  focused: boolean;
}

export interface FlattenedTreeNode {
  /** The actual tree node data */
  node: TreeNode;
  /** Depth in tree (0 = root) */
  depth: number;
  /** Index among visible nodes */
  index: number;
  /** Total siblings at this level */
  setSize: number;
  /** Position among siblings (1-indexed) */
  posInSet: number;
  /** Parent node ID or null for root */
  parentId: string | null;
  /** Node state */
  state: TreeNodeState;
  /** Whether this node has children */
  hasChildren: boolean;
  /** Unique ID for this node */
  nodeId: string;
}

// ============================================================================
// Tree View Props
// ============================================================================

export interface TreeViewProps {
  /** Tree data to render */
  data: TreeNode[];
  /** Currently selected node ID */
  selectedId: string | null;
  /** Set of expanded node IDs */
  expandedIds: Set<string>;
  /** Called when a node is selected */
  onSelect: (node: TreeNode) => void;
  /** Called when a node should expand */
  onExpand: (id: string) => void;
  /** Called when a node should collapse */
  onCollapse: (id: string) => void;
  /** Loading state */
  isLoading?: boolean;
  /** Error state */
  error?: Error | null;
  /** Optional label for the tree */
  ariaLabel?: string;
}

export interface TreeNodeProps {
  /** The flattened node data */
  flatNode: FlattenedTreeNode;
  /** Called when this node is selected */
  onSelect: () => void;
  /** Called when this node should expand */
  onExpand: () => void;
  /** Called when this node should collapse */
  onCollapse: () => void;
  /** Whether this node has keyboard focus */
  isFocused: boolean;
}

// ============================================================================
// Tree Navigation
// ============================================================================

export type TreeNavigationAction =
  | 'UP'
  | 'DOWN'
  | 'LEFT'
  | 'RIGHT'
  | 'HOME'
  | 'END'
  | 'SELECT'
  | 'EXPAND_ALL_SIBLINGS';

export interface TreeNavigationState {
  /** Currently focused node ID */
  focusedId: string | null;
  /** Currently selected node ID */
  selectedId: string | null;
  /** Set of expanded node IDs */
  expandedIds: Set<string>;
}

// ============================================================================
// Tree Filtering
// ============================================================================

export interface TreeFilter {
  /** Filter by status */
  status?: string[];
  /** Filter by priority */
  priority?: string[];
  /** Filter by hierarchy level */
  level?: HierarchyLevel[];
  /** Text search */
  searchQuery?: string;
  /** Filter by assignee */
  assignee?: string[];
  /** Show only items due within N days */
  dueWithinDays?: number;
}

// ============================================================================
// Tree Icons
// ============================================================================

export const HIERARCHY_ICONS: Record<HierarchyLevel, string> = {
  initiative: '🎯',
  project: '📁',
  epic: '🏔️',
  sprint: '🏃',
  story: '📖',
  task: '✅',
  subtask: '📋',
};

export const HIERARCHY_COLORS: Record<HierarchyLevel, string> = {
  initiative: 'text-purple-500',
  project: 'text-blue-500',
  epic: 'text-indigo-500',
  sprint: 'text-green-500',
  story: 'text-orange-500',
  task: 'text-cyan-500',
  subtask: 'text-gray-500',
};
