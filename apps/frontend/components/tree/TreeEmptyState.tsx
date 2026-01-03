import { Button } from '@/components/ui/button';
import { FolderTree, Plus } from 'lucide-react';

interface TreeEmptyStateProps {
  onCreateTask?: () => void;
  filterActive?: boolean;
  onClearFilters?: () => void;
}

export function TreeEmptyState({ onCreateTask, filterActive, onClearFilters }: TreeEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center text-muted-foreground animate-in fade-in zoom-in-95 duration-200">
      <div className="p-4 bg-muted/50 rounded-full mb-4 ring-1 ring-white/10">
        <FolderTree className="w-8 h-8 opacity-50" />
      </div>

      <h3 className="text-lg font-medium text-foreground mb-2">
        {filterActive ? 'No tasks found' : 'No tasks yet'}
      </h3>

      <p className="text-sm max-w-[250px] mb-6">
        {filterActive
          ? 'Try adjusting your filters or search terms to find what you are looking for.'
          : 'Get started by creating your first task or importing a project.'}
      </p>

      <div className="flex gap-3">
        {filterActive ? (
          <Button variant="outline" onClick={onClearFilters}>
            Clear Filters
          </Button>
        ) : (
          onCreateTask && (
            <Button onClick={onCreateTask} className="gap-2">
              <Plus className="w-4 h-4" />
              Create Task
            </Button>
          )
        )}
      </div>
    </div>
  );
}
