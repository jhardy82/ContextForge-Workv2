import {
    ContextMenu,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuLabel,
    ContextMenuSeparator,
    ContextMenuShortcut,
    ContextMenuSub,
    ContextMenuSubContent,
    ContextMenuSubTrigger,
    ContextMenuTrigger
} from '@/components/ui/context-menu';
import { Task } from '@/lib/types';
import {
    AlertTriangle,
    ArrowRight,
    Bot,
    Copy,
    Link,
    Trash2,
    Wand2
} from 'lucide-react';
import React from 'react';

interface TaskContextMenuProps {
  children: React.ReactNode;
  task: Task;
  onRunAIAction: (action: string, task: Task) => void;
  onDelete: (taskId: string) => void;
  onDuplicate: (task: Task) => void;
  onStatusChange: (taskId: string, status: string) => void;
  onEdit: (task: Task) => void;
}

export function TaskContextMenu({
  children,
  task,
  onRunAIAction,
  onDelete,
  onDuplicate,
  onStatusChange,
  onEdit
}: TaskContextMenuProps) {
  return (
    <ContextMenu>
      <ContextMenuTrigger>{children}</ContextMenuTrigger>
      <ContextMenuContent className="w-64 bg-slate-900/95 backdrop-blur-xl border border-white/10 text-slate-200 shadow-2xl rounded-xl p-1">

        {/* AI Actions Section */}
        <ContextMenuLabel className="text-cyan-400 text-xs font-medium flex items-center gap-2 px-2 py-1.5">
          <Bot size={12} className="animate-pulse" />
          AI CONSTALLATION
        </ContextMenuLabel>

        <ContextMenuItem
          onClick={() => onRunAIAction('breakdown', task)}
          className="gap-2 focus:bg-cyan-500/20 focus:text-cyan-300 rounded-lg cursor-pointer"
        >
          <Wand2 size={14} />
          Auto-Breakdown Task
          <ContextMenuShortcut>⌘B</ContextMenuShortcut>
        </ContextMenuItem>

        <ContextMenuItem
          onClick={() => onRunAIAction('blockers', task)}
          className="gap-2 focus:bg-red-500/20 focus:text-red-300 rounded-lg cursor-pointer"
        >
          <AlertTriangle size={14} />
          Find Potential Blockers
        </ContextMenuItem>

        <ContextMenuItem
          onClick={() => onRunAIAction('optimize', task)}
          className="gap-2 focus:bg-purple-500/20 focus:text-purple-300 rounded-lg cursor-pointer"
        >
          <Link size={14} />
          Suggest Dependencies
        </ContextMenuItem>

        <ContextMenuSeparator className="bg-white/10 my-1" />

        {/* Standard Actions */}
        <ContextMenuLabel className="text-slate-500 text-xs px-2 py-1.5">
            ACTIONS
        </ContextMenuLabel>

        <ContextMenuItem
           onClick={() => onEdit(task)}
           className="gap-2 focus:bg-white/10 rounded-lg font-medium text-cyan-200"
        >
          <Wand2 size={14} className="text-cyan-400" /> {/* Reusing icon for visual consistency */}
          Edit Details
        </ContextMenuItem>

        <ContextMenuSub>
          <ContextMenuSubTrigger className="gap-2 focus:bg-white/10 rounded-lg">
            <ArrowRight size={14} />
            Move to Status
          </ContextMenuSubTrigger>
          <ContextMenuSubContent className="w-48 bg-slate-900 border border-white/10 text-slate-200">
            <ContextMenuItem onClick={() => onStatusChange(task.id, 'todo')} className="focus:bg-white/10 cursor-pointer">To Do</ContextMenuItem>
            <ContextMenuItem onClick={() => onStatusChange(task.id, 'in_progress')} className="focus:bg-white/10 cursor-pointer">In Progress</ContextMenuItem>
            <ContextMenuItem onClick={() => onStatusChange(task.id, 'review')} className="focus:bg-white/10 cursor-pointer">Review</ContextMenuItem>
            <ContextMenuItem onClick={() => onStatusChange(task.id, 'done')} className="focus:bg-white/10 cursor-pointer">Done</ContextMenuItem>
            <ContextMenuItem onClick={() => onStatusChange(task.id, 'blocked')} className="focus:bg-white/10 cursor-pointer text-red-400">Blocked</ContextMenuItem>
          </ContextMenuSubContent>
        </ContextMenuSub>

        <ContextMenuItem
           onClick={() => onDuplicate(task)}
           className="gap-2 focus:bg-white/10 rounded-lg"
        >
          <Copy size={14} />
          Duplicate
        </ContextMenuItem>

        <ContextMenuSeparator className="bg-white/10 my-1" />

        <ContextMenuItem
          onClick={() => onDelete(task.id)}
          className="gap-2 text-red-400 focus:bg-red-500/10 focus:text-red-300 rounded-lg"
        >
          <Trash2 size={14} />
          Delete Task
          <ContextMenuShortcut>⌫</ContextMenuShortcut>
        </ContextMenuItem>

      </ContextMenuContent>
    </ContextMenu>
  );
}
