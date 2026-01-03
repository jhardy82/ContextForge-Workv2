/**
 * PriorityIndicator - Priority display with color coding
 */

import { cn } from '@/lib/utils';
import type { TaskPriorityValue } from '@/types/objects';
import { PRIORITY_BADGE_STYLES } from '@/types/ui';
import { AlertCircle, AlertTriangle, ArrowDown, ArrowUp } from 'lucide-react';

interface PriorityIndicatorProps {
  priority: TaskPriorityValue;
  showLabel?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

const PRIORITY_ICONS: Record<TaskPriorityValue, React.ReactNode> = {
  low: <ArrowDown className="w-3 h-3" />,
  medium: <ArrowUp className="w-3 h-3" />,
  high: <AlertCircle className="w-3 h-3" />,
  critical: <AlertTriangle className="w-3 h-3" />,
};

const PRIORITY_LABELS: Record<TaskPriorityValue, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

export function PriorityIndicator({
  priority,
  showLabel = true,
  size = 'md',
  className,
}: PriorityIndicatorProps) {
  const style = PRIORITY_BADGE_STYLES[priority];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm',
        style.bg,
        style.text,
        'border',
        style.border,
        className,
      )}
      title={PRIORITY_LABELS[priority]}
    >
      {PRIORITY_ICONS[priority]}
      {showLabel && <span>{PRIORITY_LABELS[priority]}</span>}
    </span>
  );
}
