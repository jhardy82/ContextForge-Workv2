/**
 * useVirtualization - Conditional virtualization for large trees
 */

import type { FlattenedTreeNode } from '@/types/tree';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useMemo, useRef } from 'react';

interface UseVirtualizationProps {
  /** All flattened nodes */
  items: FlattenedTreeNode[];
  /** Threshold for enabling virtualization */
  threshold?: number;
  /** Estimated item height */
  estimateSize?: number;
  /** Overscan count */
  overscan?: number;
}

interface UseVirtualizationReturn {
  /** Whether virtualization is active */
  shouldVirtualize: boolean;
  /** The virtualizer instance (null if not virtualizing) */
  virtualizer: ReturnType<typeof useVirtualizer> | null;
  /** Ref to attach to scroll container */
  parentRef: React.RefObject<HTMLDivElement>;
  /** Get virtual items (or all items if not virtualizing) */
  virtualItems: Array<{ index: number; start: number; size: number }>;
  /** Total size of all items */
  totalSize: number;
}

export function useVirtualization({
  items,
  threshold = 500,
  estimateSize = 36,
  overscan = 5,
}: UseVirtualizationProps): UseVirtualizationReturn {
  const parentRef = useRef<HTMLDivElement>(null);
  const shouldVirtualize = items.length > threshold;

  const virtualizer = useMemo(() => {
    if (!shouldVirtualize) return null;

    // We need to create the virtualizer in a useVirtualizer hook context
    // This is a workaround - in the actual component, use useVirtualizer directly
    return null;
  }, [shouldVirtualize]);

  // Placeholder virtual items for non-virtualized mode
  const nonVirtualItems = useMemo(() =>
    items.map((_, index) => ({
      index,
      start: index * estimateSize,
      size: estimateSize,
    })),
    [items, estimateSize]
  );

  return {
    shouldVirtualize,
    virtualizer,
    parentRef,
    virtualItems: nonVirtualItems,
    totalSize: items.length * estimateSize,
  };
}

/**
 * Hook to use directly in components that need virtualization
 */
export function useTreeVirtualizer(
  items: FlattenedTreeNode[],
  parentRef: React.RefObject<HTMLElement>,
  options: { threshold?: number; estimateSize?: number; overscan?: number } = {}
) {
  const { threshold = 500, estimateSize = 36, overscan = 5 } = options;
  const shouldVirtualize = items.length > threshold;

  const virtualizer = useVirtualizer({
    count: shouldVirtualize ? items.length : 0,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan,
  });

  return {
    shouldVirtualize,
    virtualizer: shouldVirtualize ? virtualizer : null,
    virtualItems: shouldVirtualize
      ? virtualizer.getVirtualItems()
      : items.map((_, index) => ({ index, start: index * estimateSize, size: estimateSize })),
    totalSize: shouldVirtualize
      ? virtualizer.getTotalSize()
      : items.length * estimateSize,
  };
}
