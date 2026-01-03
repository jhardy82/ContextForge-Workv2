
import { useUpdateTaskApiV1TasksTaskIdPut } from '@/api/generated/tasks/tasks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
} from '@/components/ui/sheet';
import { Textarea } from '@/components/ui/textarea';
import { Task } from '@/lib/types';
import { useQueryClient } from '@tanstack/react-query';
import { Trash2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

interface TaskDetailPanelProps {
  task: Task | null;
  onClose: () => void;
  onDelete: (taskId: string) => void;
}

export function TaskDetailPanel({ task, onClose, onDelete }: TaskDetailPanelProps) {
  console.debug('[DEBUG] TaskDetailPanel rendering for task:', task?.id);
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');

  // Sync state when task changes
  useEffect(() => {
    if (task) {
        setTitle(task.title || '');
        setSummary(task.summary || '');
        setDescription(task.description || '');
        setStatus(task.status);
        setPriority(task.priority || 'medium');
    }
  }, [task]);

  // Use generated Orval hook for task updates
  const updateTaskMutation = useUpdateTaskApiV1TasksTaskIdPut();

  const handleSave = async () => {
    if (!task) return;
    console.debug('[DEBUG] Saving task with updates:', { title, description, status, priority });
    try {
      await updateTaskMutation.mutateAsync({
        taskId: task.id,
        data: { title, summary, description, status, priority } as any
      });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks'] });
      toast.success('Task updated successfully');
    } catch (error) {
      console.error('[DEBUG] Failed to update task:', error);
      toast.error('Failed to update task');
    }
  };

  const isOpen = !!task;

  if (!task) return null;


  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="bg-slate-900 border-l border-white/10 text-slate-200 sm:max-w-md overflow-y-auto">
        <SheetHeader className="mb-6">
          <SheetTitle className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400">
            Task Details
          </SheetTitle>
          <SheetDescription className="text-slate-400">
            View and edit task properties.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6">
            {/* Title */}
            <div className="space-y-2">
                <Label htmlFor="title" className="text-cyan-200">Task Title</Label>
                <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="bg-slate-950/50 border-white/10 focus:border-cyan-500/50"
                />
            </div>

            {/* Summary */}
            <div className="space-y-2">
                <Label htmlFor="summary" className="text-cyan-200">Summary</Label>
                <Input
                    id="summary"
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    className="bg-slate-950/50 border-white/10 focus:border-cyan-500/50"
                />
            </div>

             {/* Status & Priority Row */}
             <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label className="text-cyan-200">Status</Label>
                     <Select value={status} onValueChange={setStatus}>
                        <SelectTrigger className="bg-slate-950/50 border-white/10">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-900 border-white/10 text-white">
                            <SelectItem value="todo">To Do</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="review">Review</SelectItem>
                            <SelectItem value="done">Done</SelectItem>
                            <SelectItem value="blocked">Blocked</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <Label className="text-cyan-200">Priority</Label>
                     <Select value={priority} onValueChange={setPriority}>
                        <SelectTrigger className="bg-slate-950/50 border-white/10">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-900 border-white/10 text-white">
                            <SelectItem value="critical" className="text-red-400">Critical</SelectItem>
                            <SelectItem value="high" className="text-orange-400">High</SelectItem>
                            <SelectItem value="medium" className="text-yellow-400">Medium</SelectItem>
                            <SelectItem value="low" className="text-blue-400">Low</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
             </div>

             {/* Description */}
            <div className="space-y-2">
                <Label htmlFor="description" className="text-cyan-200">Description</Label>
                <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="bg-slate-950/50 border-white/10 min-h-[150px] focus:border-cyan-500/50 resize-none"
                    placeholder="Add a more detailed description..."
                />
            </div>

            {/* Metadata (Read Only) */}
            <div className="p-4 rounded-lg bg-white/5 space-y-3 text-xs text-slate-400">
                <div className="flex justify-between">
                    <span>Task ID</span>
                    <span className="font-mono text-slate-300">{task.id}</span>
                </div>
                 <div className="flex justify-between">
                    <span>Created</span>
                    <span className="text-slate-300">{new Date(task.created_at || Date.now()).toLocaleDateString()}</span>
                </div>
                 {task.project_id && (
                    <div className="flex justify-between">
                        <span>Project ID</span>
                        <span className="text-slate-300">{task.project_id}</span>
                    </div>
                 )}
            </div>

        </div>

        <SheetFooter className="mt-8 flex-col gap-3 sm:flex-col">
            <Button onClick={handleSave} className="w-full bg-cyan-600 hover:bg-cyan-500 text-white">
                Save Changes
            </Button>

            <div className="flex gap-2">
                <Button variant="outline" onClick={onClose} className="flex-1 border-white/10 hover:bg-white/5 text-slate-300">
                    Cancel
                </Button>
                <Button
                    variant="destructive"
                    onClick={() => {
                        onClose();
                        onDelete(task.id);
                    }}
                    className="flex-1 bg-red-900/30 hover:bg-red-900/50 text-red-400 border border-red-900/50"
                >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete
                </Button>
            </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
