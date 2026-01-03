import { TaskCreate } from '@/api/generated/model';
import { useCreateTaskApiV1TasksPost, useDeleteTaskApiV1TasksTaskIdDelete, useListTasksApiV1TasksGet, useUpdateTaskApiV1TasksTaskIdPut } from '@/api/generated/tasks/tasks';
import { TaskDetailPanel } from '@/components/detail/TaskDetailPanel';
import { TreeView } from '@/components/tree/TreeView';
import { Button } from '@/components/ui/button';
import { AlertCircle, FolderTree, Plus, RefreshCw } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

export function GreenfieldLayoutQuery() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // generated hook for fetching tasks
  const {
    data: taskList,
    isLoading,
    isError,
    error,
    refetch
  } = useListTasksApiV1TasksGet();

  const createTaskMutation = useCreateTaskApiV1TasksPost();
  const updateTaskMutation = useUpdateTaskApiV1TasksTaskIdPut();
  const deleteTaskMutation = useDeleteTaskApiV1TasksTaskIdDelete();

  const tasks = taskList?.tasks || [];

  // Simple Flat-to-Tree logic
  const treeData = useMemo(() => {
      const taskMap = new Map<string, TreeNode>();
      const roots: TreeNode[] = [];

      // Pass 1: Create nodes
      tasks.forEach((task: any) => {
          taskMap.set(task.id, { ...task, children: [], level: task.task_type || 'task' });
      });

      // Pass 2: Connect
      tasks.forEach((task: any) => {
         const node = taskMap.get(task.id)!;
         if (task.parent_task_id && taskMap.has(task.parent_task_id)) {
             taskMap.get(task.parent_task_id)!.children!.push(node);
         } else {
             roots.push(node);
         }
      });

      return roots;
  }, [tasks]);

  const selectedTask = useMemo(() => {
     // @ts-ignore
      return tasks.find(t => t.id === selectedId) || null;
  }, [selectedId, tasks]);

  const handleSaveTask = async (taskId: string, updates: any) => {
    try {
      await updateTaskMutation.mutateAsync({ taskId, data: updates });
      toast.success("Task Updated");
      refetch();
    } catch (e) {
      console.error("Failed to update task", e);
      toast.error("Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId: string) => {
      try {
          await deleteTaskMutation.mutateAsync({ taskId });
          toast.success("Task Deleted");
          setSelectedId(null);
          refetch();
      } catch (e) {
          console.error("Failed to delete task", e);
          toast.error("Failed to delete task");
      }
  };

  // Simplified Seed for demo purposes using mutations
  const handleSmartSeed = async () => {
        const taskId = `T-gen-${Math.floor(Math.random() * 1000)}`;
        const payload: TaskCreate = {
            title: `Generated Task ${taskId}`,
            id: taskId,
            primary_project: "P-greenfield-alpha",
            status: "new",
            priority: "p2",
            task_type: "task",
            owner: "s-user"
        };

        try {
            await createTaskMutation.mutateAsync({ data: payload });
            toast.success(`Created ${taskId}`);
            refetch();
        } catch (e) {
            toast.error("Failed to create task");
            console.error(e);
        }
  };

  if (isError) {
      return (
          <div className="flex items-center justify-center h-screen bg-slate-950 text-red-400 gap-2">
              <AlertCircle />
              <span>Failed to load tasks: {error?.message}</span>
              <Button variant="outline" onClick={() => refetch()}>Retry</Button>
          </div>
      )
  }

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden text-slate-100">

      {/* SIDEBAR (Tree) */}
      <div className="w-[400px] flex flex-col border-r border-white/10 bg-slate-900/50">
        <div className="p-4 border-b border-white/5 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
                <div className="p-1.5 bg-cyan-500/10 rounded-md">
                    <FolderTree className="w-5 h-5 text-cyan-400" />
                </div>
                <h2 className="font-semibold text-sm tracking-wide text-muted-foreground">PROJECT EXPLORER (Query)</h2>
            </div>
            <div className="flex gap-1">
                <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => refetch()} title="Refresh">
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
                <Button size="icon" variant="ghost" className="h-7 w-7" onClick={handleSmartSeed} title="Quick Add">
                    <Plus className="w-4 h-4" />
                </Button>
            </div>
        </div>

        <div className="flex-1 overflow-hidden p-2">
            <TreeView
                data={treeData}
                onSelectNode={(node) => setSelectedId(node.id)}
                className="h-full"
            />
        </div>

        <div className="p-2 border-t border-white/5 bg-slate-950/30 text-[10px] text-muted-foreground text-center font-mono">
            {tasks.length} Objects • React Query Active
        </div>
      </div>

      {/* MAIN CONTENT (Detail) */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950">
         <TaskDetailPanel
            // @ts-ignore
            task={selectedTask}
            onClose={() => setSelectedId(null)}
            onSave={handleSaveTask}
            onDelete={handleDeleteTask}
         />
      </div>

    </div>
  );
}
