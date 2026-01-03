import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, X } from 'lucide-react';
import { useCallback, useState } from 'react';
import { TaskStatus } from './KanbanColumn';

interface QuickTaskFormProps {
  status: TaskStatus;
  onSubmit: (task: { title: string; priority: string; status: TaskStatus }) => Promise<void>;
  onCancel: () => void;
}

export function QuickTaskForm({ status, onSubmit, onCancel }: QuickTaskFormProps) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({ title: title.trim(), priority, status });
      setTitle('');
      setPriority('medium');
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [title, priority, status, onSubmit]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      onKeyDown={handleKeyDown}
      className="p-3 bg-card border rounded-md shadow-sm space-y-3"
    >
      <Input
        autoFocus
        placeholder="Task title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="text-sm"
        disabled={isSubmitting}
      />

      <div className="flex items-center gap-2">
        <Select value={priority} onValueChange={setPriority} disabled={isSubmitting}>
          <SelectTrigger className="w-28 h-8 text-xs">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="critical">🔴 Critical</SelectItem>
            <SelectItem value="high">🟠 High</SelectItem>
            <SelectItem value="medium">🟡 Medium</SelectItem>
            <SelectItem value="low">🔵 Low</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex-1" />

        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          <X className="w-4 h-4" />
        </Button>

        <Button
          type="submit"
          size="sm"
          disabled={!title.trim() || isSubmitting}
        >
          <Plus className="w-4 h-4 mr-1" />
          Add
        </Button>
      </div>

      <p className="text-xs text-muted-foreground">
        Press <kbd className="px-1 bg-muted rounded">Enter</kbd> to save,
        <kbd className="px-1 bg-muted rounded ml-1">Esc</kbd> to cancel
      </p>
    </form>
  );
}
