/**
 * Search Store - Manages search and filtering state
 */

import type { HierarchyLevel, TaskPriorityValue, TaskStatusValue } from '@/types/objects';
import { create } from 'zustand';

// ============================================================================
// Store Types
// ============================================================================

interface SearchFilters {
  /** Filter by status */
  status: TaskStatusValue[];
  /** Filter by priority */
  priority: TaskPriorityValue[];
  /** Filter by hierarchy level */
  level: HierarchyLevel[];
  /** Filter by assignee */
  assignee: string[];
  /** Show only items due within N days */
  dueWithinDays: number | null;
  /** Show only my tasks */
  onlyMyTasks: boolean;
  /** Show completed tasks */
  showCompleted: boolean;
}

interface SearchState {
  /** Search query string */
  query: string;
  /** Active filters */
  filters: SearchFilters;
  /** Is search focused */
  isSearchFocused: boolean;
  /** Recent searches */
  recentSearches: string[];
}

interface SearchActions {
  setQuery: (query: string) => void;
  clearQuery: () => void;

  setFilter: <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => void;
  toggleStatusFilter: (status: TaskStatusValue) => void;
  togglePriorityFilter: (priority: TaskPriorityValue) => void;
  toggleLevelFilter: (level: HierarchyLevel) => void;
  clearFilters: () => void;

  setSearchFocused: (focused: boolean) => void;
  addRecentSearch: (search: string) => void;
  clearRecentSearches: () => void;

  reset: () => void;
}

type SearchStore = SearchState & SearchActions;

// ============================================================================
// Default Values
// ============================================================================

const defaultFilters: SearchFilters = {
  status: [],
  priority: [],
  level: [],
  assignee: [],
  dueWithinDays: null,
  onlyMyTasks: false,
  showCompleted: true,
};

const initialState: SearchState = {
  query: '',
  filters: defaultFilters,
  isSearchFocused: false,
  recentSearches: [],
};

// ============================================================================
// Store Implementation
// ============================================================================

export const useSearchStore = create<SearchStore>((set, get) => ({
  ...initialState,

  setQuery: (query) => set({ query }),
  clearQuery: () => set({ query: '' }),

  setFilter: (key, value) => set((state) => ({
    filters: { ...state.filters, [key]: value },
  })),

  toggleStatusFilter: (status) => set((state) => {
    const current = state.filters.status;
    const newStatus = current.includes(status)
      ? current.filter((s) => s !== status)
      : [...current, status];
    return { filters: { ...state.filters, status: newStatus } };
  }),

  togglePriorityFilter: (priority) => set((state) => {
    const current = state.filters.priority;
    const newPriority = current.includes(priority)
      ? current.filter((p) => p !== priority)
      : [...current, priority];
    return { filters: { ...state.filters, priority: newPriority } };
  }),

  toggleLevelFilter: (level) => set((state) => {
    const current = state.filters.level;
    const newLevel = current.includes(level)
      ? current.filter((l) => l !== level)
      : [...current, level];
    return { filters: { ...state.filters, level: newLevel } };
  }),

  clearFilters: () => set({ filters: defaultFilters }),

  setSearchFocused: (focused) => set({ isSearchFocused: focused }),

  addRecentSearch: (search) => set((state) => {
    if (!search.trim()) return state;
    const filtered = state.recentSearches.filter((s) => s !== search);
    return {
      recentSearches: [search, ...filtered].slice(0, 10), // Keep last 10
    };
  }),

  clearRecentSearches: () => set({ recentSearches: [] }),

  reset: () => set(initialState),
}));

// ============================================================================
// Selectors
// ============================================================================

export const selectQuery = (state: SearchStore) => state.query;
export const selectFilters = (state: SearchStore) => state.filters;
export const selectIsSearchFocused = (state: SearchStore) => state.isSearchFocused;
export const selectRecentSearches = (state: SearchStore) => state.recentSearches;

export const selectHasActiveFilters = (state: SearchStore) => {
  const { filters } = state;
  return (
    filters.status.length > 0 ||
    filters.priority.length > 0 ||
    filters.level.length > 0 ||
    filters.assignee.length > 0 ||
    filters.dueWithinDays !== null ||
    filters.onlyMyTasks ||
    !filters.showCompleted
  );
};
