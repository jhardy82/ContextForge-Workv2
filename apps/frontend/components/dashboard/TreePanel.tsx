/**
 * TreePanel - Hierarchical tree view of projects and tasks
 */

import { TreeView } from '@/components/tree';
import { useUIStore } from '@/stores/uiStore';
import type { Project, Task, TreeNode } from '@/types/objects';
import { getNodeId } from '@/types/objects';
import { useCallback, useMemo } from 'react';

// Import sample data for initial testing
import sampleData from '@/mocks/data/sample-project.json';

interface TreePanelProps {
  /** Tasks from API */
  tasks?: Task[];
  /** Projects from API */
  projects?: Project[];
  /** Called when a task is selected */
  onTaskSelect?: (task: Task) => void;
  /** Loading state */
  isLoading?: boolean;
  /** Error state */
  error?: Error | null;
}

/**
 * Convert API data to TreeNode format
 */
function convertToTreeNodes(data: typeof sampleData): TreeNode[] {
  // Return initiatives as root nodes
  return data.initiatives as unknown as TreeNode[];
}

export function TreePanel({
  tasks = [],
  projects = [],
  onTaskSelect,
  isLoading = false,
  error = null,
}: TreePanelProps) {
  // Use UI store for expansion and selection state
  const {
    selectedId,
    expandedIds,
    select,
    expand,
    collapse,
  } = useUIStore();

  // Convert sample data to tree nodes for demo
  // In production, this would merge API tasks/projects
  const treeData = useMemo<TreeNode[]>(() => {
    // Use sample data for now
    return convertToTreeNodes(sampleData);
  }, []);

  // Handle node selection
  const handleSelect = useCallback((node: TreeNode) => {
    const nodeId = getNodeId(node);
    select(nodeId);

    // If it's a task, also call the parent handler
    if (node.type === 'task' && onTaskSelect) {
      onTaskSelect(node as unknown as Task);
    }
  }, [select, onTaskSelect]);

  // Handle expand
  const handleExpand = useCallback((id: string) => {
    expand(id);
  }, [expand]);

  // Handle collapse
  const handleCollapse = useCallback((id: string) => {
    collapse(id);
  }, [collapse]);

  return (
    <div className="h-full flex flex-col bg-slate-900/50 rounded-xl border border-white/10">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <h2 className="text-sm font-semibold text-cyan-200">Project Hierarchy</h2>
        <span className="text-xs text-slate-400">
          {treeData.length} root items
        </span>
      </div>

      {/* Tree View */}
      <div className="flex-1 overflow-hidden">
        <TreeView
          data={treeData}
          selectedId={selectedId}
          expandedIds={expandedIds}
          onSelect={handleSelect}
          onExpand={handleExpand}
          onCollapse={handleCollapse}
          isLoading={isLoading}
          error={error}
          ariaLabel="Project and task hierarchy"
        />
      </div>
    </div>
  );
}
