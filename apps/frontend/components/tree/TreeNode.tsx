import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { FlattenedTreeNode, HIERARCHY_COLORS, HIERARCHY_ICONS } from '@/types/tree';
import { ChevronDown, ChevronRight } from 'lucide-react';
import React, { memo } from 'react';

interface TreeNodeProps {
  flatNode: FlattenedTreeNode;
  style: React.CSSProperties;
  onSelect: (nodeId: string) => void;
  onToggle: (nodeId: string) => void;
  isFocused: boolean;
}

export const TreeNode = memo(({ flatNode, style, onSelect, onToggle, isFocused }: TreeNodeProps) => {
  const { node, depth, expanded, selected, hasChildren, nodeId } = flatNode;

  return (
    <div
      style={style}
      className={cn(
        "flex items-center gap-2 px-2 py-1 text-sm border-l-2 cursor-pointer transition-colors outline-none select-none group",
        selected ? "bg-accent/50 border-cyan-500" : "border-transparent hover:bg-muted/30",
        isFocused ? "ring-1 ring-cyan-400 ring-inset" : ""
      )}
      onClick={() => onSelect(nodeId)}
      onDoubleClick={() => hasChildren && onToggle(nodeId)}
      role="treeitem"
      aria-expanded={hasChildren ? expanded : undefined}
      aria-selected={selected}
      aria-level={depth + 1}
      tabIndex={isFocused ? 0 : -1}
      data-node-id={nodeId}
      data-testid={`tree-node-${nodeId}`}
    >
      {/* Indentation */}
      <div style={{ width: `${depth * 20}px` }} className="shrink-0" />

      {/* Expand/Collapse Toggle */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onToggle(nodeId);
        }}
        className={cn(
          "p-0.5 rounded-sm hover:bg-muted text-muted-foreground transition-transform duration-200",
          !hasChildren && "opacity-0 pointer-events-none"
        )}
        tabIndex={-1}
        aria-hidden="true"
      >
        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Node Icon */}
      <span className={cn("shrink-0", HIERARCHY_COLORS[node.level])} aria-hidden="true">
        {HIERARCHY_ICONS[node.level]}
      </span>

      {/* Title */}
      <span className={cn(
        "truncate font-medium transition-colors",
        selected ? "text-foreground" : "text-muted-foreground group-hover:text-foreground"
      )}>
        {node.title}
      </span>

      {/* Meta Badges (Progressive) */}
      <div className="ml-auto flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <Badge variant={node.status === 'done' ? 'default' : 'secondary'} className="text-[10px] h-5 px-1.5 uppercase tracking-wider">
          {node.status}
        </Badge>
        {node.priority === 'critical' && (
           <Badge variant="destructive" className="text-[10px] h-5 px-1.5">CRR</Badge>
        )}
      </div>
    </div>
  );
}, (prev, next) => {
  // Custom comparison for performance optimization
  return (
    prev.flatNode.nodeId === next.flatNode.nodeId &&
    prev.flatNode.expanded === next.flatNode.expanded &&
    prev.flatNode.selected === next.flatNode.selected &&
    prev.isFocused === next.isFocused &&
    prev.style.top === next.style.top
  );
});
