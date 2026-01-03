/**
 * DetailHeader - Header with title, badges, and "Show Advanced" toggle
 */

import { PriorityIndicator } from '@/components/shared/PriorityIndicator';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import type { Task } from '@/types/objects';
import { HIERARCHY_ICONS } from '@/types/tree';
import { Settings2, X } from 'lucide-react';

interface DetailHeaderProps {
  task: Task;
  showAdvanced: boolean;
  onToggleAdvanced: () => void;
  onClose: () => void;
}

export function DetailHeader({
  task,
  showAdvanced,
  onToggleAdvanced,
  onClose,
}: DetailHeaderProps) {
  const icon = HIERARCHY_ICONS[task.type] || HIERARCHY_ICONS.task;

  return (
    <div className="flex flex-col gap-3 pb-4 border-b border-white/10">
      {/* Top row: close button and advanced toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span>{icon}</span>
          <span className="font-mono">{task.task_id}</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Switch
              id="show-advanced"
              checked={showAdvanced}
              onCheckedChange={onToggleAdvanced}
            />
            <Label
              htmlFor="show-advanced"
              className="text-xs text-slate-400 cursor-pointer flex items-center gap-1"
            >
              <Settings2 className="w-3 h-3" />
              Show Advanced
            </Label>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-slate-400 hover:text-slate-200"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Title */}
      <h2 className="text-xl font-bold text-slate-100 leading-tight">
        {task.title}
      </h2>

      {/* Badges row */}
      <div className="flex flex-wrap gap-2">
        <StatusBadge status={task.status} size="sm" />
        <PriorityIndicator priority={task.priority} size="sm" />
        {task.task_type && (
          <span className="inline-flex items-center px-2 py-0.5 text-xs rounded-full bg-slate-700 text-slate-300">
            {task.task_type}
          </span>
        )}
        {task.assignee && (
          <span className="inline-flex items-center px-2 py-0.5 text-xs rounded-full bg-cyan-900/30 text-cyan-300 border border-cyan-500/30">
            👤 {task.assignee}
          </span>
        )}
        {task.due_date && (
          <span className="inline-flex items-center px-2 py-0.5 text-xs rounded-full bg-orange-900/30 text-orange-300 border border-orange-500/30">
            📅 {new Date(task.due_date).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}
