import { Task } from '@/lib/types';
import { cn } from '@/lib/utils';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { AlertCircle, CheckCircle2, Clock, GripVertical } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onClick: () => void;
  onRunAIAction: (action: string, task: Task) => void;
  onDelete: (taskId: string) => void;
  onDuplicate: (task: Task) => void;
  onStatusChange: (taskId: string, status: string) => void;
}

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'border-l-red-500',
  high: 'border-l-orange-500',
  medium: 'border-l-yellow-500',
  low: 'border-l-blue-500',
  none: 'border-l-gray-300',
};

const PRIORITY_ICONS: Record<string, React.ReactNode> = {
  critical: <AlertCircle className="w-3 h-3 text-red-500" />,
  high: <AlertCircle className="w-3 h-3 text-orange-500" />,
  medium: <Clock className="w-3 h-3 text-yellow-500" />,
  low: <CheckCircle2 className="w-3 h-3 text-blue-500" />,
};

import { TaskContextMenu } from './TaskContextMenu';

export function TaskCard({ task, onClick,  onRunAIAction,
  onDelete,
  onDuplicate,
  onStatusChange
}: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const priority = task.priority || 'none';


  const content = (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "group bg-card border rounded-md shadow-sm cursor-pointer",
        "hover:shadow-md hover:border-primary/50 transition-all",
        "border-l-4",
        PRIORITY_COLORS[priority],
        isDragging && "opacity-50 shadow-lg rotate-2"
      )}
      onClick={onClick}
    >
      <div className="p-3">
        {/* Header with drag handle and title */}
        <div className="flex items-start gap-2">
          <button
            {...attributes}
            {...listeners}
            className="mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing"
            onClick={(e) => e.stopPropagation()}
          >
            <GripVertical className="w-4 h-4 text-muted-foreground" />
          </button>

          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm text-foreground truncate">
              {task.title || task.name}
            </h4>

            {task.description && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {task.description}
              </p>
            )}
          </div>
        </div>

        {/* Footer with metadata */}
        <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/50">
          <div className="flex items-center gap-2">
            {PRIORITY_ICONS[priority] && (
              <span title={`Priority: ${priority}`}>
                {PRIORITY_ICONS[priority]}
              </span>
            )}

            {task.project_id && (
              <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                #{task.project_id.slice(0, 6)}
              </span>
            )}
          </div>

          {task.due_date && (
            <span className="text-xs text-muted-foreground">
              {new Date(task.due_date).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <TaskContextMenu
      task={task}
      onRunAIAction={onRunAIAction}
      onDelete={onDelete}
      onDuplicate={onDuplicate}

      onStatusChange={onStatusChange}
      onEdit={() => onClick()}
    >
      {content}
    </TaskContextMenu>
  );
}
