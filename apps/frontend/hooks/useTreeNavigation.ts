/**
 * useTreeNavigation - Keyboard navigation for ARIA tree pattern
 */

import type { FlattenedTreeNode, TreeNavigationAction } from '@/types/tree';
import { useCallback, useEffect } from 'react';

interface UseTreeNavigationProps {
  /** Flattened visible nodes for navigation */
  flattenedNodes: FlattenedTreeNode[];
  /** Currently focused node ID */
  focusedId: string | null;
  /** Set of expanded node IDs */
  expandedIds: Set<string>;
  /** Callback when focus changes */
  onFocusChange: (id: string | null) => void;
  /** Callback when selection changes */
  onSelect: (id: string) => void;
  /** Callback when a node should expand */
  onExpand: (id: string) => void;
  /** Callback when a node should collapse */
  onCollapse: (id: string) => void;
  /** Whether the tree has keyboard focus */
  isTreeFocused: boolean;
}

interface UseTreeNavigationReturn {
  /** Handle keydown events */
  handleKeyDown: (event: React.KeyboardEvent) => void;
  /** Get the index of a node by ID */
  getNodeIndex: (id: string) => number;
  /** Navigate to a specific node */
  navigateTo: (id: string) => void;
}

export function useTreeNavigation({
  flattenedNodes,
  focusedId,
  expandedIds,
  onFocusChange,
  onSelect,
  onExpand,
  onCollapse,
  isTreeFocused,
}: UseTreeNavigationProps): UseTreeNavigationReturn {

  const getNodeIndex = useCallback((id: string): number => {
    return flattenedNodes.findIndex((node) => node.nodeId === id);
  }, [flattenedNodes]);

  const getFocusedIndex = useCallback((): number => {
    if (!focusedId) return -1;
    return getNodeIndex(focusedId);
  }, [focusedId, getNodeIndex]);

  const navigateTo = useCallback((id: string) => {
    onFocusChange(id);
    // Scroll into view will be handled by the component
  }, [onFocusChange]);

  const handleAction = useCallback((action: TreeNavigationAction) => {
    const currentIndex = getFocusedIndex();
    const currentNode = currentIndex >= 0 ? flattenedNodes[currentIndex] : null;

    switch (action) {
      case 'DOWN': {
        // Move to next visible node
        if (currentIndex < flattenedNodes.length - 1) {
          navigateTo(flattenedNodes[currentIndex + 1].nodeId);
        }
        break;
      }

      case 'UP': {
        // Move to previous visible node
        if (currentIndex > 0) {
          navigateTo(flattenedNodes[currentIndex - 1].nodeId);
        }
        break;
      }

      case 'RIGHT': {
        if (!currentNode) break;

        if (currentNode.hasChildren && !expandedIds.has(currentNode.nodeId)) {
          // Expand if collapsed and has children
          onExpand(currentNode.nodeId);
        } else if (currentNode.hasChildren && expandedIds.has(currentNode.nodeId)) {
          // Move to first child if expanded
          const nextIndex = currentIndex + 1;
          if (nextIndex < flattenedNodes.length &&
              flattenedNodes[nextIndex].depth > currentNode.depth) {
            navigateTo(flattenedNodes[nextIndex].nodeId);
          }
        }
        break;
      }

      case 'LEFT': {
        if (!currentNode) break;

        if (currentNode.hasChildren && expandedIds.has(currentNode.nodeId)) {
          // Collapse if expanded
          onCollapse(currentNode.nodeId);
        } else if (currentNode.parentId) {
          // Move to parent
          navigateTo(currentNode.parentId);
        }
        break;
      }

      case 'HOME': {
        // Move to first node
        if (flattenedNodes.length > 0) {
          navigateTo(flattenedNodes[0].nodeId);
        }
        break;
      }

      case 'END': {
        // Move to last visible node
        if (flattenedNodes.length > 0) {
          navigateTo(flattenedNodes[flattenedNodes.length - 1].nodeId);
        }
        break;
      }

      case 'SELECT': {
        if (currentNode) {
          onSelect(currentNode.nodeId);
        }
        break;
      }

      case 'EXPAND_ALL_SIBLINGS': {
        // Expand all siblings at current level
        if (!currentNode) break;

        flattenedNodes
          .filter((node) =>
            node.depth === currentNode.depth &&
            node.parentId === currentNode.parentId &&
            node.hasChildren
          )
          .forEach((node) => onExpand(node.nodeId));
        break;
      }
    }
  }, [flattenedNodes, getFocusedIndex, navigateTo, expandedIds, onExpand, onCollapse, onSelect]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (!isTreeFocused) return;

    let action: TreeNavigationAction | null = null;

    switch (event.key) {
      case 'ArrowDown':
        action = 'DOWN';
        break;
      case 'ArrowUp':
        action = 'UP';
        break;
      case 'ArrowRight':
        action = 'RIGHT';
        break;
      case 'ArrowLeft':
        action = 'LEFT';
        break;
      case 'Home':
        action = 'HOME';
        break;
      case 'End':
        action = 'END';
        break;
      case 'Enter':
      case ' ':
        action = 'SELECT';
        break;
      case '*':
        action = 'EXPAND_ALL_SIBLINGS';
        break;
      default:
        // Handle typeahead search (first letter navigation)
        if (event.key.length === 1 && !event.ctrlKey && !event.altKey && !event.metaKey) {
          const char = event.key.toLowerCase();
          const currentIndex = getFocusedIndex();

          // Find next node starting with this character
          for (let i = 1; i <= flattenedNodes.length; i++) {
            const index = (currentIndex + i) % flattenedNodes.length;
            const node = flattenedNodes[index];
            const title = 'title' in node.node ? node.node.title : ('name' in node.node ? node.node.name : '');
            if (title?.toLowerCase().startsWith(char)) {
              navigateTo(node.nodeId);
              event.preventDefault();
              break;
            }
          }
        }
        return;
    }

    if (action) {
      event.preventDefault();
      handleAction(action);
    }
  }, [isTreeFocused, handleAction, getFocusedIndex, flattenedNodes, navigateTo]);

  // Set initial focus if none exists
  useEffect(() => {
    if (isTreeFocused && !focusedId && flattenedNodes.length > 0) {
      onFocusChange(flattenedNodes[0].nodeId);
    }
  }, [isTreeFocused, focusedId, flattenedNodes, onFocusChange]);

  return {
    handleKeyDown,
    getNodeIndex,
    navigateTo,
  };
}
