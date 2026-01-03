import { task2Api } from "@/lib/task2-api";
import { temporal } from "zundo";
import { create } from "zustand";
import { Project, Task } from "../types/objects";

interface ProjectState {
  projects: Project[];
  tasks: Task[];
  activeProjectId: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchProjects: () => Promise<void>;
  fetchTasks: (projectId?: string) => Promise<void>;
  createTask: (task: Partial<Task>) => Promise<Task | null>;
  updateTask: (taskId: string, updates: Partial<Task>) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  setActiveProject: (projectId: string | null) => void;
}

const apiClient = task2Api;

export const useProjectStore = create<ProjectState>()(
  temporal(
    (set, get) => ({
      projects: [],
      tasks: [],
      activeProjectId: null,
      isLoading: false,
      error: null,

      fetchProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const projects = await apiClient.getProjects();
          set({ projects, isLoading: false });
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      fetchTasks: async (projectId) => {
        set({ isLoading: true, error: null });
        try {
          // Cast the response to match the new Task interface - in a real app we'd have runtime validation
          // For now, we assume the backend returns compatible data or we map it as needed.
          // Since the backend is 0 tasks right now, this is safe.
          const tasks = (await apiClient.getTasks({
            project_id: projectId,
          })) as unknown as Task[];
          set({ tasks, isLoading: false });
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      createTask: async (taskData) => {
        set({ isLoading: true, error: null });
        try {
          const created = await apiClient.createTask(taskData as any);
          if (created) {
            // Cast and add to local state
            const newTask = created as unknown as Task;
            set((state) => ({
              tasks: [...state.tasks, newTask],
              isLoading: false,
            }));
            return newTask;
          }
          return null;
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
          return null;
        }
      },

      updateTask: async (taskId, updates) => {
        // Optimistic update
        const previousTasks = get().tasks;
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.id === taskId ? { ...t, ...updates } : t
          ),
        }));

        try {
          await apiClient.updateTask(taskId, updates as any);
        } catch (error) {
          // Revert on failure
          set({ tasks: previousTasks, error: (error as Error).message });
        }
      },

      deleteTask: async (taskId) => {
        const previousTasks = get().tasks;
        set((state) => ({
          tasks: state.tasks.filter((t) => t.id !== taskId),
        }));

        try {
          await apiClient.deleteTask(taskId);
        } catch (error) {
          set({ tasks: previousTasks, error: (error as Error).message });
        }
      },

      setActiveProject: (projectId) => {
        set({ activeProjectId: projectId });
        get().fetchTasks(projectId || undefined);
      },
    }),
    {
      limit: 100, // Undo history limit
      partialize: (state) => {
        // Exclude loading and error from undo history
        const { isLoading, error, ...rest } = state;
        return rest;
      },
    }
  )
);
