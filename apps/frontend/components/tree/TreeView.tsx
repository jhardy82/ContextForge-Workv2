import { TreeNode } from '@/types/objects';
import { FlattenedTreeNode } from '@/types/tree';
import { useVirtualizer } from '@tanstack/react-virtual';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { TreeEmptyState } from './TreeEmptyState';
import { TreeNode as TreeNodeComponent } from './TreeNode';
import { TreeSkeleton } from './TreeSkeleton';

interface TreeViewProps {
  data: TreeNode[];
  isLoading?: boolean;
  onSelectNode?: (node: TreeNode) => void;
  className?: string;
}

export function TreeView({ data, isLoading, onSelectNode, className }: TreeViewProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  // State
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusedId, setFocusedId] = useState<string | null>(null);

  // Flatten the tree based on expansion state
  const flattenedData = useMemo(() => {
    const flattened: FlattenedTreeNode[] = [];

    const flatten = (nodes: TreeNode[], depth = 0, parentId: string | null = null) => {
      nodes.forEach((node, index) => {
        const isExpanded = expandedIds.has(node.id);

        flattened.push({
          node,
          depth,
          index: flattened.length,
          setSize: nodes.length,
          posInSet: index + 1,
          parentId,
          state: {
            expanded: isExpanded,
            selected: selectedId === node.id,
            focused: focusedId === node.id,
          },
          hasChildren: !!(node.children && node.children.length > 0),
          nodeId: node.id,
        });

        if (isExpanded && node.children) {
          flatten(node.children, depth + 1, node.id);
        }
      });
    };

    flatten(data);
    return flattened;
  }, [data, expandedIds, selectedId, focusedId]);

  // Virtualizer
  const rowVirtualizer = useVirtualizer({
    count: flattenedData.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 28, // Compact row height
    overscan: 5,
  });

  // Handlers
  const handleToggle = (nodeId: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  const handleSelect = (nodeId: string) => {
    setSelectedId(nodeId);
    setFocusedId(nodeId);

    const node = flattenedData.find(n => n.nodeId === nodeId)?.node;
    if (node && onSelectNode) {
      onSelectNode(node);
    }
  };

  // Keyboard Navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!focusedId) return;

    const currentIndex = flattenedData.findIndex(n => n.nodeId === focusedId);
    if (currentIndex === -1) return;

    const currentNode = flattenedData[currentIndex];

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (currentIndex < flattenedData.length - 1) {
          const nextId = flattenedData[currentIndex + 1].nodeId;
          setFocusedId(nextId);
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (currentIndex > 0) {
          const prevId = flattenedData[currentIndex - 1].nodeId;
          setFocusedId(prevId);
        }
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (currentNode.hasChildren) {
          if (currentNode.state.expanded) {
            // Already expanded, move to first child if exists
             if (currentIndex < flattenedData.length - 1) {
                const nextNode = flattenedData[currentIndex + 1];
                if (nextNode.depth > currentNode.depth) {
                   setFocusedId(nextNode.nodeId);
                }
             }
          } else {
            handleToggle(currentNode.nodeId);
          }
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (currentNode.hasChildren && currentNode.state.expanded) {
           handleToggle(currentNode.nodeId); // Collapse
        } else if (currentNode.parentId) {
           // Move to parent
           setFocusedId(currentNode.parentId);
        }
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        handleSelect(focusedId);
        break;
    }
  };

  // Auto-scroll to focused item
  useEffect(() => {
    if (focusedId && parentRef.current) {
        // Simple logic: If we have virtualizer scrollTo, use it
        const index = flattenedData.findIndex(n => n.nodeId === focusedId);
        if (index !== -1) {
            rowVirtualizer.scrollToIndex(index);
        }
    }
  }, [focusedId, flattenedData, rowVirtualizer]);


  if (isLoading) return <TreeSkeleton />;
  if (data.length === 0) return <TreeEmptyState />;

  return (
    <div
      ref={parentRef}
      className={`h-full overflow-auto outline-none ${className}`}
      role="tree"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onFocus={() => {
         if (!focusedId && flattenedData.length > 0) {
             setFocusedId(flattenedData[0].nodeId);
         }
      }}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const node = flattenedData[virtualRow.index];
          return (
            <TreeNodeComponent
              key={node.nodeId}
              flatNode={node}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
              onSelect={handleSelect}
              onToggle={handleToggle}
              isFocused={focusedId === node.nodeId}
            />
          );
        })}
      </div>
    </div>
  );
}
