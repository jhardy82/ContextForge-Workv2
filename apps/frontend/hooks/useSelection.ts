/**
 * useSelection - Selection state management with multi-select support
 */

import { useCallback, useState } from 'react';

interface UseSelectionProps {
  /** Enable multi-select */
  multiSelect?: boolean;
  /** Callback when selection changes */
  onSelectionChange?: (selectedIds: Set<string>) => void;
}

interface UseSelectionReturn {
  /** Currently selected IDs */
  selectedIds: Set<string>;
  /** Last selected ID (for shift-select range) */
  lastSelectedId: string | null;
  /** Check if an ID is selected */
  isSelected: (id: string) => boolean;
  /** Select a single item (clears others unless ctrl/shift) */
  select: (id: string, event?: { ctrlKey?: boolean; shiftKey?: boolean; metaKey?: boolean }) => void;
  /** Toggle selection of an item */
  toggle: (id: string) => void;
  /** Select multiple items */
  selectMultiple: (ids: string[]) => void;
  /** Clear all selections */
  clearSelection: () => void;
  /** Select all provided items */
  selectAll: (ids: string[]) => void;
}

export function useSelection({
  multiSelect = false,
  onSelectionChange,
}: UseSelectionProps = {}): UseSelectionReturn {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [lastSelectedId, setLastSelectedId] = useState<string | null>(null);

  const updateSelection = useCallback((newSelection: Set<string>) => {
    setSelectedIds(newSelection);
    onSelectionChange?.(newSelection);
  }, [onSelectionChange]);

  const isSelected = useCallback((id: string): boolean => {
    return selectedIds.has(id);
  }, [selectedIds]);

  const select = useCallback((
    id: string,
    event?: { ctrlKey?: boolean; shiftKey?: boolean; metaKey?: boolean }
  ) => {
    if (!multiSelect || (!event?.ctrlKey && !event?.shiftKey && !event?.metaKey)) {
      // Single select - clear others
      updateSelection(new Set([id]));
      setLastSelectedId(id);
    } else if (event?.ctrlKey || event?.metaKey) {
      // Toggle selection (cmd/ctrl click)
      const newSelection = new Set(selectedIds);
      if (newSelection.has(id)) {
        newSelection.delete(id);
      } else {
        newSelection.add(id);
      }
      updateSelection(newSelection);
      setLastSelectedId(id);
    }
    // Note: Shift-select for range would require knowing the flat list order
    // That would need to be passed in from the tree component
  }, [multiSelect, selectedIds, updateSelection]);

  const toggle = useCallback((id: string) => {
    const newSelection = new Set(selectedIds);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    updateSelection(newSelection);
  }, [selectedIds, updateSelection]);

  const selectMultiple = useCallback((ids: string[]) => {
    if (!multiSelect) {
      // In single-select mode, only select the last one
      if (ids.length > 0) {
        updateSelection(new Set([ids[ids.length - 1]]));
        setLastSelectedId(ids[ids.length - 1]);
      }
    } else {
      updateSelection(new Set(ids));
      if (ids.length > 0) {
        setLastSelectedId(ids[ids.length - 1]);
      }
    }
  }, [multiSelect, updateSelection]);

  const clearSelection = useCallback(() => {
    updateSelection(new Set());
    setLastSelectedId(null);
  }, [updateSelection]);

  const selectAll = useCallback((ids: string[]) => {
    if (multiSelect) {
      updateSelection(new Set(ids));
    }
  }, [multiSelect, updateSelection]);

  return {
    selectedIds,
    lastSelectedId,
    isSelected,
    select,
    toggle,
    selectMultiple,
    clearSelection,
    selectAll,
  };
}
