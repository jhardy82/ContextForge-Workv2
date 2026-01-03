import { Task, TaskStatus } from '@/lib/types';
import { cn } from '@/lib/utils';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { TaskCard } from './TaskCard';

// Re-export TaskStatus for convenience
export type { TaskStatus } from '@/lib/types';

interface KanbanColumnProps {
  id: TaskStatus;
  title: string;
  tasks: Task[];
  color: string;
  onTaskClick: (task: Task) => void;
  onQuickCreate?: (status: TaskStatus) => void;
  onRunAIAction: (action: string, task: Task) => void;
  onDelete: (taskId: string) => void;
  onDuplicate: (task: Task) => void;
  onStatusChange: (taskId: string, status: string) => void;
}

const STATUS_LIMITS: Partial<Record<TaskStatus, number>> = {
  new: Infinity,
  todo: Infinity,
  in_progress: 5,
  review: 3,
  done: Infinity,
  blocked: Infinity,
};

export function KanbanColumn({
  id,
  title,
  tasks,
  color,
  onTaskClick,
  onQuickCreate,
  onRunAIAction,
  onDelete,
  onDuplicate,
  onStatusChange
}: KanbanColumnProps) {
  const { isOver, setNodeRef } = useDroppable({ id });
  const limit = STATUS_LIMITS[id] ?? Infinity;
  const isOverLimit = limit !== Infinity && tasks.length >= limit;

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "flex flex-col w-72 min-w-72 glass rounded-xl transition-all duration-300",
        isOver && "ring-2 ring-cyan-400 ring-offset-2 ring-offset-transparent bg-white/10"
      )}
    >
      {/* Column Header */}
      <div className={cn("p-4 rounded-t-xl border-b border-white/5", "bg-gradient-to-r from-transparent via-white/5 to-transparent")}>
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-sm tracking-wide text-white/90 uppercase">{title}</h3>
          <div className="flex items-center gap-2">
            <span className={cn(
              "px-2 py-0.5 rounded-full text-xs font-medium",
              isOverLimit ? "bg-red-500/20 text-red-200" : "bg-white/20 text-white"
            )}>
              {tasks.length}{limit !== Infinity && `/${limit}`}
            </span>
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="flex-1 p-3 space-y-3 overflow-y-auto max-h-[calc(100vh-280px)] scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        <SortableContext items={tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onClick={() => onTaskClick(task)}
              onRunAIAction={onRunAIAction}
              onDelete={onDelete}
              onDuplicate={onDuplicate}
              onStatusChange={onStatusChange}
            />
          ))}
        </SortableContext>

        {tasks.length === 0 && (
          <div className="p-4 text-center text-muted-foreground text-sm">
            No tasks
          </div>
        )}
      </div>

      {/* Quick Add Button */}
      {onQuickCreate && (
        <button
          onClick={() => onQuickCreate(id)}
          className="m-2 p-2 text-sm text-muted-foreground/60 hover:text-cyan-400 hover:bg-white/5 rounded-md transition-all flex items-center justify-center gap-1 border border-dashed border-white/10 hover:border-cyan-400/50"
        >
          <span className="text-lg">+</span>
          <span>Add task</span>
        </button>
      )}
    </div>
  );
}
