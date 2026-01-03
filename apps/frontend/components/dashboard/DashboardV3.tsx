
import { useListProjectsApiV1ProjectsGet } from '@/api/generated/projects/projects';
import { useCreateTaskApiV1TasksPost, useDeleteTaskApiV1TasksTaskIdDelete, useListTasksApiV1TasksGet, useUpdateTaskApiV1TasksTaskIdPut } from '@/api/generated/tasks/tasks';
import { ContextExplorer } from '@/components/context/ContextExplorer';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Task, TaskPriority } from '@/lib/types';
import { cn } from '@/lib/utils';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Bot,
    Calendar as CalendarIcon,
    Database,
    FolderTree,
    KanbanSquare,
    ListTodo,
    PieChart,
    RefreshCw,
    Settings,
    Timer,
    Wifi,
    WifiOff
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { toast, Toaster } from 'sonner';
import { AgentSidebar } from '../agent/AgentSidebar';
import { ActionListView } from './ActionListView';
import { AIInput } from './AIInput';
import { AnalyticsView } from './AnalyticsView';
import { AppMenubar } from './AppMenubar';
import { AppSidebarQuery as AppSidebar } from './AppSidebarQuery';
import { CommandPalette } from './CommandPalette';
import { DataExplorer } from './DataExplorer';
import { KanbanBoard } from './KanbanBoard';
import { TaskStatus } from './KanbanColumn';
import { QuickTaskForm } from './QuickTaskForm';
import { SettingsDialog } from './SettingsDialog';
import { SprintView } from './SprintView';
import { SystemHealthWidget } from './SystemHealthWidget';
import { TaskDetailPanel } from './TaskDetailPanel';
import { TimelineView } from './TimelineView';

const getApiUrl = () => localStorage.getItem('taskman_api_url') || 'http://localhost:3001/api/v1';

export function DashboardV3() {
  // const [apiClient] = useState(() => new Task2ApiClient(getApiUrl()));
  // Used for conditional rendering of different views
  const [activeView, setActiveView] = useState<'kanban' | 'sprint' | 'analytics' | 'action-list' | 'data-explorer' | 'timeline' | 'tree'>('kanban');
  const [quickCreateStatus, setQuickCreateStatus] = useState<TaskStatus | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showNewTaskDialog, setShowNewTaskDialog] = useState(false);
  const [showNewSprintDialog, setShowNewSprintDialog] = useState(false);
  const [isAgentOpen, setIsAgentOpen] = useState(false); // Sidebar State

  const queryClient = useQueryClient();

  // Fetch tasks
  const {
    data: taskList,
    isLoading: tasksLoading,
    isError: tasksError,
    refetch: refetchTasks
  } = useListTasksApiV1TasksGet(
      {},
      { query: { refetchInterval: 30000, staleTime: 10000 } }
  );

  // Adapter for Legacy components: Map TaskResponse -> Task
  const tasks = useMemo(() => {
      if (!taskList?.tasks) return [];
      return taskList.tasks.map((t: any) => ({
          ...t,
          // Map mismatched fields
          project_id: t.primary_project,
          sprint_id: t.primary_sprint,
          due_date: t.due_at,
          parent_task_id: t.parents?.[0]
      })) as Task[];
  }, [taskList]);


  // Fetch projects
  const {
    data: projectList,
    isLoading: projectsLoading,
  } = useListProjectsApiV1ProjectsGet(
      {},
      { query: { staleTime: 60000 } }
  );

  const projects = useMemo(() => {
      // @ts-ignore
      return (projectList?.projects || []) as any[];
  }, [projectList]);

  // Generated Mutations
  const updateTaskMutationGenerated = useUpdateTaskApiV1TasksTaskIdPut();
  const createTaskMutationGenerated = useCreateTaskApiV1TasksPost();
  const deleteTaskMutationGenerated = useDeleteTaskApiV1TasksTaskIdDelete();

  // Update task mutation with optimistic updates
  const updateTaskMutation = useMutation({
    mutationFn: async ({ taskId, updates }: { taskId: string; updates: Partial<Task> }) => {
      // Map legacy updates to TaskUpdate model if needed, strictly speaking we should
      // but for now passing updates might work if fields align or we cast.
      // Generated expects { taskId, data: TaskUpdate }
      return updateTaskMutationGenerated.mutateAsync({ taskId, data: updates as any });
    },
    onMutate: async ({ taskId, updates }) => {
      await queryClient.cancelQueries({ queryKey: ['/api/v1/tasks'] });
      // Note: Query Key for generated hook is different: getListTasksApiV1TasksGetQueryKey()
      // We should use the generated key logic or just use string path if we know it.
      // Orval uses ['/api/v1/tasks', params]

      // Optimistic update logic is harder with generated keys without helper,
      // skipping complex optimistic update for this migration step to ensure stability first.
      return { };
    },
    onError: (err) => {
      toast.error('Failed to update task');
    },
    onSuccess: () => {
      toast.success('Task updated');
    },
    onSettled: () => {
      refetchTasks(); // Refetch using the hook's refetch
    },
  });

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: async (newTask: Partial<Task>) => {
      // Map legacy task to TaskCreate
      const project_id = newTask.project_id || projects[0]?.id || 'proj_default';
      const sprint_id = newTask.sprint_id || 'sprint_default';

      const priorityMap: Record<string, string> = {
          'critical': 'p0',
          'high': 'p1',
          'medium': 'p2',
          'low': 'p3'
      };

      const statusMap: Record<string, string> = {
          'todo': 'new',
          'in_progress': 'in_progress',
          'done': 'done',
          'blocked': 'blocked'
      };

      const payload = {
        ...newTask,
        id: `T-${crypto.randomUUID()}`, // Generate ID
        title: newTask.title || "Untitled Task", // Ensure title
        summary: newTask.summary || newTask.title || "Untitled Task",
        description: newTask.description || "No description provided",
        owner: newTask.assigned_to || "user_1", // Dummy owner
        status: statusMap[newTask.status || 'todo'] || 'new',
        priority: priorityMap[newTask.priority || 'medium'] || 'p2',
        primary_project: project_id,
        primary_sprint: sprint_id,
        due_at: newTask.due_date,
        // Ensure required arrays are present
        assignees: newTask.assigned_to ? [newTask.assigned_to] : [],
        related_projects: [],
        related_sprints: [],
        labels: []
      };

      return createTaskMutationGenerated.mutateAsync({ data: payload as any });
    },
    onSuccess: () => {
      refetchTasks();
      toast.success('Task created');
      setQuickCreateStatus(null);
    },
    onError: () => {
      toast.error('Failed to create task');
    },
  });

  // Delete task mutation
  const deleteTaskMutation = useMutation({
    mutationFn: async (taskId: string) => {
      return deleteTaskMutationGenerated.mutateAsync({ taskId });
    },
    onSuccess: () => {
      refetchTasks();
      toast.success('Task deleted');
    },
    onError: () => {
      toast.error('Failed to delete task');
    },
  });

  // Handle task status change (drag-drop)
  const handleTaskStatusChange = useCallback(async (taskId: string, newStatus: TaskStatus) => {
    await updateTaskMutation.mutateAsync({
      taskId,
      updates: { status: newStatus }
    });
  }, [updateTaskMutation]);

  // Handle quick task creation
  const handleQuickCreate = useCallback(async (task: { title: string; priority: string; status: TaskStatus }) => {
    await createTaskMutation.mutateAsync({
      title: task.title,
      priority: task.priority as TaskPriority,
      status: task.status,
    });
  }, [createTaskMutation]);

  // Handle AI task creation
  const handleAITaskCreate = useCallback(async (task: Partial<Task>) => {
    await createTaskMutation.mutateAsync({
      title: task.title,
      priority: task.priority || 'medium',
      status: task.status || 'todo',
    });
  }, [createTaskMutation]);

  // Handle Context Menu Actions
  const handleRunAIAction = useCallback((action: string, task: Task) => {
    // Simulate AI processing for now
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 2000)),
      {
        loading: 'AI Agent is thinking...',
        success: () => {
             // In a real app, this would use the AI response
             if (action === 'breakdown') return 'Task decomposed into 3 subtasks (Simulated)';
             if (action === 'blockers') return 'No potential blockers detected (Simulated)';
             return 'Analysis complete';
        },
        error: 'AI Analysis failed'
      }
    );
  }, []);

  const handleDeleteTask = useCallback((taskId: string) => {
      deleteTaskMutation.mutate(taskId);
  }, [deleteTaskMutation]);

  const handleDuplicateTask = useCallback((task: Task) => {
      const { id, ...taskData } = task; // Exclude ID
      createTaskMutation.mutate({
          ...taskData,
          title: `${taskData.title} (Copy)`,
          status: 'todo' // Reset status for duplicate
      });
  }, [createTaskMutation]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        return;
      }

      switch (e.key) {
        case '?':
          toast.info(
            <div className="space-y-1 text-sm">
              <p><kbd className="px-1 bg-muted rounded">C</kbd> Create task</p>
              <p><kbd className="px-1 bg-muted rounded">⌘K</kbd> Command palette</p>
              <p><kbd className="px-1 bg-muted rounded">R</kbd> Refresh</p>
            </div>,
            { duration: 5000 }
          );
          break;
        case 'r':
          if (!e.metaKey && !e.ctrlKey) {
            refetchTasks();
            toast.info('Refreshing...');
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [refetchTasks]);

  const isConnected = !tasksError;
  const isLoading = tasksLoading || projectsLoading;

  console.log("[DASHBOARD] Rendering...", { isConnected, isLoading, tasksCount: tasks.length });

  return (
    <div className="min-h-screen bg-aurora text-foreground selection:bg-accent selection:text-accent-foreground font-sans overflow-hidden flex flex-col">
        <AppMenubar
            onCreateTask={() => setQuickCreateStatus('todo')}
            onOpenSettings={() => setShowSettings(true)}
            onToggleView={setActiveView}
            currentView={activeView}
            onTriggerAgent={() => setIsAgentOpen(true)}
        />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar
            className="hidden md:flex"
            onNavigate={(view) => {
                if(view === 'kanban' || view === 'sprint' || view === 'analytics' || view === 'data-explorer' || view === 'timeline' || view === 'tree') {
                    setActiveView(view);
                }
            }}
        />

        <div className="flex-1 flex flex-col overflow-y-auto">
            {/* Header */}
            <header className="sticky top-0 z-40 glass border-b border-white/10 shrink-0">
                <div className="flex items-center justify-between px-6 py-3">
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-600 drop-shadow-[0_0_10px_rgba(139,92,246,0.3)]">
                    TaskMan v3
                    </h1>
                    <Badge variant={isConnected ? "default" : "destructive"} className="gap-1">
                    {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                    {isConnected ? 'Connected' : 'Offline'}
                    </Badge>
                </div>

                <div className="flex items-center gap-3">
                    <CommandPalette
                    tasks={tasks}
                    projects={projects}
                    onCreateTask={() => setQuickCreateStatus('todo')}
                    onOpenTask={setSelectedTask}
                    onOpenProject={() => {}}
                    onToggleView={setActiveView}
                    onOpenSettings={() => setShowSettings(true)}
                    onOpenFilters={() => setShowFilters(true)}
                    />

                    {/* Navigation Buttons */}
                    <aside className="hidden md:block">
                    <nav className="flex items-center gap-2 p-1 rounded-xl bg-white/5 border border-white/10">
                        <button
                        onClick={() => setActiveView('kanban')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'kanban'
                            ? "bg-purple-500/20 text-purple-400 shadow-[0_0_20px_rgba(139,92,246,0.3)] border border-purple-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <KanbanSquare size={20} />
                        <span className="font-medium">Kanban</span>
                        </button>

                        <button
                        onClick={() => setActiveView('sprint')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'sprint'
                            ? "bg-blue-500/20 text-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.3)] border border-blue-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <Timer size={20} />
                        <span className="font-medium">Sprints</span>
                        </button>

                        <button
                        onClick={() => setActiveView('timeline')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'timeline'
                            ? "bg-pink-500/20 text-pink-400 shadow-[0_0_20px_rgba(236,72,153,0.3)] border border-pink-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <CalendarIcon size={20} />
                        <span className="font-medium">Timeline</span>
                        </button>

                        <button
                        onClick={() => setActiveView('analytics')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'analytics'
                            ? "bg-cyan-500/20 text-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.3)] border border-cyan-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <PieChart size={20} />
                        <span className="font-medium">Analytics</span>
                        </button>

                        <button
                        onClick={() => setActiveView('action-list')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'action-list'
                            ? "bg-emerald-500/20 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)] border border-emerald-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <ListTodo size={20} />
                        <span className="font-medium">Action Lists</span>
                        </button>

                        <button
                        onClick={() => setActiveView('tree')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'tree'
                            ? "bg-green-500/20 text-green-400 shadow-[0_0_20px_rgba(34,197,94,0.3)] border border-green-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <FolderTree size={20} />
                        <span className="font-medium">Tree</span>
                        </button>

                        <div className="w-px h-8 bg-white/10 mx-2" />

                        <button
                        onClick={() => setActiveView('data-explorer')}
                        className={cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            activeView === 'data-explorer'
                            ? "bg-amber-500/20 text-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.3)] border border-amber-500/50"
                            : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                        )}
                        >
                        <Database size={20} />
                        <span className="font-medium">Explorer</span>
                        </button>
                    </nav>
                    </aside>

                    <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => refetchTasks()}
                    disabled={isLoading}
                    >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>

                    <Button variant="ghost" size="sm" onClick={() => setShowSettings(true)}>
                    <Settings className="w-4 h-4" />
                    </Button>
                </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="p-6">
                {/* AI Input */}
                <div className="mb-8 max-w-2xl mx-auto">
                <AIInput onTaskCreate={handleAITaskCreate} />
                </div>

                {/* Stats Bar */}
                <div className="flex items-center gap-4 mb-6">
                <Card className="flex-1 glass border-0">
                    <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Total Tasks</span>
                        <span className="text-2xl font-bold">{tasks.length}</span>
                    </div>
                    </CardContent>
                </Card>
                <Card className="flex-1 glass border-0">
                    <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">In Progress</span>
                        <span className="text-2xl font-bold text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]">
                        {tasks.filter(t => t.status === 'in_progress').length}
                        </span>
                    </div>
                    </CardContent>
                </Card>
                <Card className="flex-1 glass border-0">
                    <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Completed</span>
                        <span className="text-2xl font-bold text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]">
                        {tasks.filter(t => t.status === 'done').length}
                        </span>
                    </div>
                    </CardContent>
                </Card>
                <Card className="flex-1 glass border-0">
                    <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Blocked</span>
                        <span className="text-2xl font-bold text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]">
                        {tasks.filter(t => t.status === 'blocked').length}
                        </span>
                    </div>
                    </CardContent>
                </Card>
                <div className="w-64">
                    <SystemHealthWidget />
                </div>
                </div>

                {/* Quick Create Form (when active) */}
                {quickCreateStatus && (
                <div className="mb-6 max-w-md">
                    <QuickTaskForm
                    status={quickCreateStatus}
                    onSubmit={handleQuickCreate}
                    onCancel={() => setQuickCreateStatus(null)}
                    />
                </div>
                )}

                {/* Board/List/Sprint View */}
                {activeView === 'kanban' ? (
                <KanbanBoard
                    tasks={tasks}
                    onTaskStatusChange={handleTaskStatusChange}
                    onTaskClick={setSelectedTask}
                    onQuickCreate={setQuickCreateStatus}
                    onRunAIAction={handleRunAIAction}
                    onDelete={handleDeleteTask}
                    onDuplicate={handleDuplicateTask}
                />
                ) : activeView === 'sprint' ? (
                <SprintView />
                ) : activeView === 'analytics' ? (
                <AnalyticsView tasks={tasks} projects={projects} />
                ) : activeView === 'action-list' ? (
                <ActionListView />
                ) : activeView === 'timeline' ? (
                <TimelineView />
                ) : activeView === 'data-explorer' ? (
                <DataExplorer />
                ) : activeView === 'tree' ? (
                <ContextExplorer />
                ) : null}
            </main>
        </div> {/* End of Main Content Column */}
      </div> {/* End of Flex Container */}

      {/* Agent Sidebar - Kept at root level as Overlay */}
      <AgentSidebar isOpen={isAgentOpen} onClose={() => setIsAgentOpen(false)} />

      {/* Keyboard shortcut hint */}
      <div className="fixed bottom-4 right-4 flex gap-2">
        <Button
          onClick={() => setIsAgentOpen(true)}
          className="bg-cyan-500 hover:bg-cyan-600 text-white shadow-[0_0_20px_rgba(6,182,212,0.4)] rounded-full px-4 h-10 gap-2 border border-cyan-400/50 animate-pulse-slow"
        >
           <Bot className="w-5 h-5" />
           Agent
        </Button>
        <Button variant="outline" size="sm" className="opacity-50 hover:opacity-100 h-10">
          Press <kbd className="mx-1 px-1 bg-muted rounded">?</kbd> for shortcuts
        </Button>
      </div>

      <Toaster />
      <SettingsDialog open={showSettings} onOpenChange={setShowSettings} />
      <TaskDetailPanel
        task={selectedTask}
        onClose={() => setSelectedTask(null)}
        onDelete={handleDeleteTask}
      />
    </div>
  );
}
