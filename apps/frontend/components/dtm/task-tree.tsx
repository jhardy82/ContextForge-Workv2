import { useState } from 'react';
import { ChevronDown, ChevronRight, Folder, FolderOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Project, Task, SACRED_GEOMETRY_SHAPES, STATUS_COLORS } from '@/lib/types';
import { cn } from '@/lib/utils';

interface TaskTreeProps {
  projects: Project[];
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  selectedTaskId?: string;
}

interface ProjectNodeProps {
  project: Project;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  selectedTaskId?: string;
}

function ProjectNode({ project, tasks, onTaskClick, selectedTaskId }: ProjectNodeProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const projectTasks = tasks.filter(task => task.project_id === project.id);
  
  const getStatusCounts = () => {
    return projectTasks.reduce((acc, task) => {
      acc[task.status] = (acc[task.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  };

  const statusCounts = getStatusCounts();

  return (
    <div className="mb-2">
      <Button
        variant="ghost"
        className="w-full justify-start h-auto p-2 hover:bg-muted/50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {projectTasks.length > 0 ? (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 flex-shrink-0" />
            ) : (
              <ChevronRight className="h-4 w-4 flex-shrink-0" />
            )
          ) : (
            <div className="w-4 h-4 flex-shrink-0" />
          )}
          
          {isExpanded ? (
            <FolderOpen className="h-4 w-4 flex-shrink-0 text-primary" />
          ) : (
            <Folder className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
          )}
          
          <div className="min-w-0 flex-1">
            <div className="font-medium text-sm truncate">{project.name}</div>
            <div className="text-xs text-muted-foreground truncate">
              {project.id} • {projectTasks.length} tasks
            </div>
          </div>
          
          <div className="flex items-center gap-1 flex-shrink-0">
            <Badge
              variant={project.status === 'active' ? 'default' : 'secondary'}
              className="text-xs"
            >
              {project.status}
            </Badge>
          </div>
        </div>
      </Button>

      {isExpanded && projectTasks.length > 0 && (
        <div className="ml-6 mt-1 space-y-1">
          {/* Status summary */}
          <div className="flex items-center gap-1 px-2 py-1 text-xs text-muted-foreground">
            {Object.entries(statusCounts).map(([status, count]) => (
              <Badge
                key={status}
                variant="outline"
                className={cn(
                  "text-xs px-1 py-0",
                  `text-${STATUS_COLORS[status as keyof typeof STATUS_COLORS]}`
                )}
              >
                {count} {status.replace('_', ' ')}
              </Badge>
            ))}
          </div>
          
          {/* Task list */}
          {projectTasks.map(task => (
            <TaskNode
              key={task.id}
              task={task}
              onClick={onTaskClick}
              isSelected={selectedTaskId === task.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface TaskNodeProps {
  task: Task;
  onClick: (task: Task) => void;
  isSelected: boolean;
}

function TaskNode({ task, onClick, isSelected }: TaskNodeProps) {
  const shapeIcon = task.shape ? SACRED_GEOMETRY_SHAPES[task.shape] : '📋';
  const statusColor = STATUS_COLORS[task.status];

  return (
    <Button
      variant="ghost"
      className={cn(
        "w-full justify-start h-auto p-2 hover:bg-muted/50",
        isSelected && "bg-accent/20 border border-accent/50"
      )}
      onClick={() => onClick(task)}
    >
      <div className="flex items-center gap-2 min-w-0 flex-1">
        <div className="w-4 h-4 flex-shrink-0" />
        
        <span className="text-lg flex-shrink-0" title={task.shape || 'No shape'}>
          {shapeIcon}
        </span>
        
        <div className="min-w-0 flex-1">
          <div className="font-medium text-sm truncate">{task.title}</div>
          <div className="text-xs text-muted-foreground truncate">
            {task.id}
            {task.priority && (
              <span className="ml-2">
                Priority: {task.priority}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-1 flex-shrink-0">
          <div
            className={cn(
              "w-2 h-2 rounded-full",
              `bg-${statusColor}`
            )}
            title={task.status.replace('_', ' ')}
          />
          <Badge
            variant="outline"
            className={cn(
              "text-xs",
              `text-${statusColor}`
            )}
          >
            {task.status.replace('_', ' ')}
          </Badge>
        </div>
      </div>
    </Button>
  );
}

export default function TaskTree({ projects, tasks, onTaskClick, selectedTaskId }: TaskTreeProps) {
  if (projects.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Folder className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p className="text-sm">No projects found</p>
        <p className="text-xs mt-1">Check your DTM API connection</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <div className="px-3 py-2 text-xs font-medium text-muted-foreground border-b">
        PROJECTS ({projects.length})
      </div>
      <div className="px-2 py-2">
        {projects.map(project => (
          <ProjectNode
            key={project.id}
            project={project}
            tasks={tasks}
            onTaskClick={onTaskClick}
            selectedTaskId={selectedTaskId}
          />
        ))}
      </div>
    </div>
  );
}