/**
 * DetailEmptyState - Empty state for detail panel
 */

import { FileText } from 'lucide-react';

interface DetailEmptyStateProps {
  message?: string;
}

export function DetailEmptyState({
  message = 'Select an item to view details',
}: DetailEmptyStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center h-full p-8 text-center"
      role="status"
      aria-label={message}
    >
      <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center mb-4">
        <FileText className="w-8 h-8 text-slate-400" />
      </div>
      <p className="text-slate-400 text-sm">{message}</p>
      <p className="text-slate-500 text-xs mt-2">
        Click on a task, project, or epic in the tree to see its details here.
      </p>
    </div>
  );
}
