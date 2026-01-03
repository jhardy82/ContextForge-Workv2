/**
 * UI Store - Manages UI state including selection, expansion, and field visibility
 */

import type {
    DialogState,
    FieldVisibility,
    SidebarState,
    ViewMode
} from '@/types/ui';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ============================================================================
// Store Types
// ============================================================================

interface UIState {
  /** Currently selected node ID */
  selectedId: string | null;
  /** Currently focused node ID (for keyboard nav) */
  focusedId: string | null;
  /** Set of expanded node IDs */
  expandedIds: Set<string>;
  /** Field visibility preferences (progressive disclosure) */
  fieldVisibility: FieldVisibility;
  /** Current view mode */
  viewMode: ViewMode;
  /** Sidebar state */
  sidebarState: SidebarState;
  /** Detail panel open */
  detailPanelOpen: boolean;
  /** Dialog states */
  dialogs: DialogState;
  /** Search query */
  searchQuery: string;
  /** Live announcement for screen readers */
  announcement: string;
}

interface UIActions {
  // Selection
  select: (id: string | null) => void;
  focus: (id: string | null) => void;
  clearSelection: () => void;

  // Expansion
  expand: (id: string) => void;
  collapse: (id: string) => void;
  toggle: (id: string) => void;
  expandAll: (ids: string[]) => void;
  collapseAll: () => void;

  // Field visibility (progressive disclosure)
  toggleAdvanced: () => void;
  setFieldVisibility: <K extends keyof FieldVisibility>(key: K, value: boolean) => void;
  resetFieldVisibility: () => void;

  // View mode
  setViewMode: (mode: ViewMode) => void;

  // Sidebar
  setSidebarState: (state: SidebarState) => void;
  toggleSidebar: () => void;

  // Detail panel
  openDetailPanel: () => void;
  closeDetailPanel: () => void;
  toggleDetailPanel: () => void;

  // Dialogs
  openDialog: (dialog: keyof DialogState) => void;
  closeDialog: (dialog: keyof DialogState) => void;
  closeAllDialogs: () => void;

  // Search
  setSearchQuery: (query: string) => void;

  // Announcements
  announce: (message: string) => void;

  // Reset
  reset: () => void;
}

type UIStore = UIState & UIActions;

// ============================================================================
// Default Values
// ============================================================================

const defaultFieldVisibility: FieldVisibility = {
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

const defaultDialogState: DialogState = {
  createTask: false,
  createProject: false,
  settings: false,
  deleteConfirm: false,
  commandPalette: false,
};

const initialState: Omit<UIState, 'expandedIds'> = {
  selectedId: null,
  focusedId: null,
  fieldVisibility: defaultFieldVisibility,
  viewMode: 'tree',
  sidebarState: 'expanded',
  detailPanelOpen: false,
  dialogs: defaultDialogState,
  searchQuery: '',
  announcement: '',
};

// ============================================================================
// Store Implementation
// ============================================================================

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      expandedIds: new Set<string>(),

      // Selection
      select: (id) => set({ selectedId: id, detailPanelOpen: id !== null }),
      focus: (id) => set({ focusedId: id }),
      clearSelection: () => set({ selectedId: null, focusedId: null }),

      // Expansion
      expand: (id) => set((state) => ({
        expandedIds: new Set([...state.expandedIds, id]),
      })),

      collapse: (id) => set((state) => {
        const newIds = new Set(state.expandedIds);
        newIds.delete(id);
        return { expandedIds: newIds };
      }),

      toggle: (id) => {
        const { expandedIds, expand, collapse } = get();
        if (expandedIds.has(id)) {
          collapse(id);
        } else {
          expand(id);
        }
      },

      expandAll: (ids) => set((state) => ({
        expandedIds: new Set([...state.expandedIds, ...ids]),
      })),

      collapseAll: () => set({ expandedIds: new Set() }),

      // Field visibility
      toggleAdvanced: () => set((state) => ({
        fieldVisibility: {
          ...state.fieldVisibility,
          showAdvanced: !state.fieldVisibility.showAdvanced,
        },
      })),

      setFieldVisibility: (key, value) => set((state) => ({
        fieldVisibility: {
          ...state.fieldVisibility,
          [key]: value,
        },
      })),

      resetFieldVisibility: () => set({ fieldVisibility: defaultFieldVisibility }),

      // View mode
      setViewMode: (mode) => set({ viewMode: mode }),

      // Sidebar
      setSidebarState: (state) => set({ sidebarState: state }),
      toggleSidebar: () => set((state) => ({
        sidebarState: state.sidebarState === 'expanded' ? 'collapsed' : 'expanded',
      })),

      // Detail panel
      openDetailPanel: () => set({ detailPanelOpen: true }),
      closeDetailPanel: () => set({ detailPanelOpen: false }),
      toggleDetailPanel: () => set((state) => ({ detailPanelOpen: !state.detailPanelOpen })),

      // Dialogs
      openDialog: (dialog) => set((state) => ({
        dialogs: { ...state.dialogs, [dialog]: true },
      })),

      closeDialog: (dialog) => set((state) => ({
        dialogs: { ...state.dialogs, [dialog]: false },
      })),

      closeAllDialogs: () => set({ dialogs: defaultDialogState }),

      // Search
      setSearchQuery: (query) => set({ searchQuery: query }),

      // Announcements
      announce: (message) => set({ announcement: message }),

      // Reset
      reset: () => set({ ...initialState, expandedIds: new Set() }),
    }),
    {
      name: 'taskman-ui-store',
      partialize: (state) => ({
        fieldVisibility: state.fieldVisibility,
        viewMode: state.viewMode,
        sidebarState: state.sidebarState,
        // Convert Set to Array for JSON serialization
        expandedIds: Array.from(state.expandedIds),
      }),
      merge: (persistedState: unknown, currentState) => {
        const persisted = persistedState as Partial<UIState & { expandedIds: string[] }> | undefined;
        return {
          ...currentState,
          ...persisted,
          // Convert Array back to Set
          expandedIds: new Set(persisted?.expandedIds ?? []),
        };
      },
    }
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const selectSelectedId = (state: UIStore) => state.selectedId;
export const selectFocusedId = (state: UIStore) => state.focusedId;
export const selectExpandedIds = (state: UIStore) => state.expandedIds;
export const selectFieldVisibility = (state: UIStore) => state.fieldVisibility;
export const selectViewMode = (state: UIStore) => state.viewMode;
export const selectSidebarState = (state: UIStore) => state.sidebarState;
export const selectDetailPanelOpen = (state: UIStore) => state.detailPanelOpen;
export const selectSearchQuery = (state: UIStore) => state.searchQuery;
export const selectShowAdvanced = (state: UIStore) => state.fieldVisibility.showAdvanced;
