/**
 * StatusBadge - Status display with WCAG AA compliant colors
 */

import { cn } from '@/lib/utils';
import type { TaskStatusValue } from '@/types/objects';
import { STATUS_BADGE_STYLES } from '@/types/ui';

interface StatusBadgeProps {
  status: TaskStatusValue;
  size?: 'sm' | 'md';
  className?: string;
}

const STATUS_LABELS: Record<TaskStatusValue, string> = {
  new: 'New',
  pending: 'Pending',
  in_progress: 'In Progress',
  done: 'Done',
  blocked: 'Blocked',
  cancelled: 'Cancelled',
};

export function StatusBadge({ status, size = 'md', className }: StatusBadgeProps) {
  const style = STATUS_BADGE_STYLES[status];

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2.5 py-1 text-sm',
        style.bg,
        style.text,
        'border',
        style.border,
        className,
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
