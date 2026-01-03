import {
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
} from '@/components/ui/command';
import { Project, Task } from '@/lib/types';
import {
    BarChart3,
    CheckSquare,
    Database,
    Filter,
    FolderOpen,
    Keyboard,
    LayoutGrid,
    List,
    Plus,
    Search,
    Settings
} from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

interface CommandPaletteProps {
  tasks: Task[];
  projects: Project[];
  onCreateTask: () => void;
  onOpenTask: (task: Task) => void;
  onOpenProject: (project: Project) => void;
  onToggleView: (view: 'kanban' | 'sprint' | 'analytics' | 'action-list' | 'data-explorer') => void;
  onOpenSettings: () => void;
  onOpenFilters: () => void;
}

export function CommandPalette({
  tasks,
  projects,
  onCreateTask,
  onOpenTask,
  onOpenProject,
  onToggleView,
  onOpenSettings,
  onOpenFilters,
}: CommandPaletteProps) {
  const [open, setOpen] = useState(false);

  // Global keyboard shortcut
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      // Cmd+K or Ctrl+K
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }

      // 'C' to create task (when not in input)
      if (e.key === 'c' && !open &&
          !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault();
        onCreateTask();
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [open, onCreateTask]);

  const handleSelect = useCallback((callback: () => void) => {
    setOpen(false);
    callback();
  }, []);

  return (
    <>
      {/* Command button hint */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground bg-muted rounded-md hover:bg-muted/80 transition-colors"
      >
        <Search className="w-4 h-4" />
        <span>Search...</span>
        <kbd className="ml-2 px-1.5 py-0.5 text-xs bg-background border rounded">
          ⌘K
        </kbd>
      </button>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>

          {/* Quick Actions */}
          <CommandGroup heading="Quick Actions">
            <CommandItem onSelect={() => handleSelect(onCreateTask)}>
              <Plus className="mr-2 h-4 w-4" />
              <span>Create new task</span>
              <kbd className="ml-auto text-xs text-muted-foreground">C</kbd>
            </CommandItem>
            <CommandItem onSelect={() => handleSelect(() => onToggleView('kanban'))}>
              <LayoutGrid className="mr-2 h-4 w-4" />
              <span>Switch to Kanban view</span>
            </CommandItem>
            <CommandItem onSelect={() => handleSelect(() => onToggleView('action-list'))}>
              <List className="mr-2 h-4 w-4" />
              <span>Switch to List view</span>
            </CommandItem>
            <CommandItem onSelect={() => handleSelect(onOpenFilters)}>
              <Filter className="mr-2 h-4 w-4" />
              <span>Open filters</span>
            </CommandItem>
            <CommandItem onSelect={() => handleSelect(() => onToggleView('data-explorer'))}>
              <Database className="mr-2 h-4 w-4" />
              <span>Switch to Data Explorer</span>
            </CommandItem>
            <CommandItem onSelect={() => handleSelect(() => onToggleView('analytics'))}>
              <BarChart3 className="mr-2 h-4 w-4" />
              <span>Switch to Analytics</span>
            </CommandItem>
            <CommandItem onSelect={() => handleSelect(onOpenSettings)}>
              <Settings className="mr-2 h-4 w-4" />
              <span>Open settings</span>
            </CommandItem>
          </CommandGroup>

          <CommandSeparator />

          {/* Recent Tasks */}
          {tasks.length > 0 && (
            <CommandGroup heading="Tasks">
              {tasks.slice(0, 5).map((task) => (
                <CommandItem
                  key={task.id}
                  onSelect={() => handleSelect(() => onOpenTask(task))}
                >
                  <CheckSquare className="mr-2 h-4 w-4" />
                  <span className="truncate">{task.title}</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {task.status}
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
          )}

          {/* Projects */}
          {projects.length > 0 && (
            <>
              <CommandSeparator />
              <CommandGroup heading="Projects">
                {projects.slice(0, 5).map((project) => (
                  <CommandItem
                    key={project.id}
                    onSelect={() => handleSelect(() => onOpenProject(project))}
                  >
                    <FolderOpen className="mr-2 h-4 w-4" />
                    <span>{project.name}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            </>
          )}

          <CommandSeparator />

          {/* Keyboard Shortcuts Help */}
          <CommandGroup heading="Keyboard Shortcuts">
            <CommandItem disabled>
              <Keyboard className="mr-2 h-4 w-4" />
              <span>Press ? to view all shortcuts</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}
