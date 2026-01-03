import { Task } from '@/lib/types';
import {
    closestCorners,
    DndContext,
    DragEndEvent,
    DragOverlay,
    DragStartEvent,
    PointerSensor,
    useSensor,
    useSensors,
} from '@dnd-kit/core';
import { useCallback, useState } from 'react';
import { KanbanColumn, TaskStatus } from './KanbanColumn';
import { TaskCard } from './TaskCard';

interface KanbanBoardProps {
  tasks: Task[];
  onRunAIAction: (action: string, task: Task) => void;
  onDelete: (taskId: string) => void;
  onDuplicate: (task: Task) => void;
  onTaskStatusChange: (taskId: string, status: TaskStatus) => void;
  onTaskClick: (task: Task) => void;
  onQuickCreate: (status: TaskStatus) => void;
}

const COLUMNS: { id: TaskStatus; title: string; color: string }[] = [
  { id: 'new', title: 'To Do', color: 'bg-slate-600' },
  { id: 'in_progress', title: 'In Progress', color: 'bg-blue-600' },
  { id: 'review', title: 'In Review', color: 'bg-purple-600' },
  { id: 'done', title: 'Completed', color: 'bg-green-600' },
  { id: 'blocked', title: 'Blocked', color: 'bg-red-600' },
];

export function KanbanBoard({
  tasks,
  onTaskStatusChange,
  onTaskClick,
  onQuickCreate,
  onRunAIAction,
  onDelete,
  onDuplicate
}: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const getTasksByStatus = useCallback((status: TaskStatus): Task[] => {
    return tasks.filter(task => {
      // Map various status formats to our canonical statuses
      let taskStatus = (task.status || 'new').toLowerCase().replace(/\s+/g, '_');
      if (taskStatus === 'todo') taskStatus = 'new';
      return taskStatus === status;
    });
  }, [tasks]);

  const handleDragStart = (event: DragStartEvent) => {
    const task = tasks.find(t => t.id === event.active.id);
    if (task) {
      setActiveTask(task);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const taskId = active.id as string;
    const newStatus = over.id as TaskStatus;

    // Find the task being dragged
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    // Check if status actually changed
    const currentStatus = (task.status || 'todo').toLowerCase().replace(/\s+/g, '_');
    if (currentStatus === newStatus) return;

    // Update the task status
    try {
      await onTaskStatusChange(taskId, newStatus);
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map((column) => (
          <KanbanColumn
            key={column.id}
            id={column.id}
            title={column.title}
            color={column.color}
            tasks={getTasksByStatus(column.id)}
            onTaskClick={onTaskClick}
            onQuickCreate={onQuickCreate}
              onRunAIAction={onRunAIAction}
              onDelete={onDelete}
              onDuplicate={onDuplicate}
              onStatusChange={(id, status) => onTaskStatusChange(id, status as TaskStatus)}
            />
        ))}
      </div>

      <DragOverlay>
        {activeTask && (
          <div className="rotate-3 scale-105">
            <TaskCard
              task={activeTask}
              onClick={() => {}}
              onRunAIAction={onRunAIAction}
              onDelete={onDelete}
              onDuplicate={onDuplicate}
              onStatusChange={(id, status) => onTaskStatusChange(id, status as TaskStatus)}
            />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  );
}
