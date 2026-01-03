import { useListActionListsApiV1ActionListsGet } from '@/api/generated/action-lists/action-lists';
import { useListProjectsApiV1ProjectsGet } from '@/api/generated/projects/projects';
import { useListSprintsApiV1SprintsGet } from '@/api/generated/sprints/sprints';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { useQueryClient } from '@tanstack/react-query';
import {
    Calendar as CalendarIcon,
    ChevronDown,
    ChevronRight,
    Folder,
    Inbox,
    LayoutGrid,
    ListTodo,
    RefreshCw,
    Star,
    Timer
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

interface AppSidebarProps {
  className?: string;
  onNavigate?: (view: string) => void;
}

const ProjectTreeItem = ({ project, collapsed }: { project: any, collapsed: boolean }) => {
  console.debug('[DEBUG] ProjectTreeItem rendering for:', project?.id);
  const [expanded, setExpanded] = useState(false);

  // Fetch children only when expanded using Orval hooks
  const { data: sprintList } = useListSprintsApiV1SprintsGet(
    { project_id: project.id },
    { query: { enabled: expanded && !collapsed } }
  );

  const { data: actionListCollection } = useListActionListsApiV1ActionListsGet(
    { project_id: project.id } as any,
    { query: { enabled: expanded && !collapsed } }
  );

  // Map to arrays for compatibility
  const sprints = useMemo(() => sprintList?.sprints || [], [sprintList]);
  const actionLists = useMemo(() => actionListCollection?.action_lists || [], [actionListCollection]);

  if (collapsed) {
    return (
      <Button variant="ghost" className="w-full justify-start gap-3 text-slate-400 hover:text-slate-200" title={project.name}>
        <Folder size={18} />
      </Button>
    );
  }

  return (
    <div className="space-y-1">
      <Button
        variant="ghost"
        className="w-full justify-between group px-2"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3 overflow-hidden">
            <Folder size={18} className="text-purple-400" />
            <span className="truncate">{project.name}</span>
        </div>
        {expanded ? <ChevronDown size={14} className="opacity-50" /> : <ChevronRight size={14} className="opacity-0 group-hover:opacity-50" />}
      </Button>

      {expanded && (
          <div className="pl-4 space-y-1 border-l border-white/5 ml-4">
              {/* Sprints */}
              {sprints.map((sprint: any) => (
                  <Button
                    key={sprint.id}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start gap-2 text-slate-500 hover:text-cyan-400 h-8 font-normal"
                  >
                      <Timer size={14} />
                      <span className="truncate">{sprint.name}</span>
                  </Button>
              ))}

              {/* Action Lists */}
              {actionLists.map((list: any) => (
                  <Button
                    key={list.id}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start gap-2 text-slate-500 hover:text-emerald-400 h-8 font-normal"
                  >
                      <ListTodo size={14} />
                      <span className="truncate">{list.name}</span>
                  </Button>
              ))}

              {sprints.length === 0 && actionLists.length === 0 && (
                  <div className="text-xs text-slate-600 px-2 py-1 italic">No items found</div>
              )}
          </div>
      )}
    </div>
  );
};

export function AppSidebar({ className, onNavigate }: AppSidebarProps) {
  console.debug('[DEBUG] AppSidebar rendering');
  const [collapsed, setCollapsed] = useState(false);
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch projects using Orval hook
  const { data: projectList } = useListProjectsApiV1ProjectsGet();
  const projects = useMemo(() => projectList?.projects || [], [projectList]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries();
    toast.success('Data synchronized');
    setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <aside className={cn("w-64 border-r border-white/10 bg-slate-900/30 backdrop-blur-xl flex flex-col transition-all duration-300", collapsed && "w-16", className)}>
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        {!collapsed && <span className="font-semibold text-sm text-slate-400">Navigation</span>}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-4">

          {/* Main Group */}
          <div className="space-y-1">
             <Button variant="ghost" className="w-full justify-start gap-3" onClick={() => onNavigate?.('kanban')}>
                <Inbox size={18} />
                {!collapsed && <span>Inbox</span>}
             </Button>
             <Button variant="ghost" className="w-full justify-start gap-3 text-cyan-400 bg-cyan-500/10" onClick={() => onNavigate?.('kanban')}>
                <Star size={18} />
                {!collapsed && <span>My Tasks</span>}
             </Button>
             <Button variant="ghost" className="w-full justify-start gap-3" onClick={() => onNavigate?.('timeline')}>
                <CalendarIcon size={18} />
                {!collapsed && <span>Timeline</span>}
             </Button>
          </div>

          <div className="flex items-center justify-between px-4 mt-6 mb-2">
             {!collapsed && <div className="text-xs font-semibold text-slate-500">PROJECTS</div>}
             {!collapsed && (
                <button
                  onClick={handleRefresh}
                  className={cn("text-slate-500 hover:text-white transition-colors", isRefreshing && "animate-spin")}
                  title="Refresh Data"
                >
                    <RefreshCw size={12} />
                </button>
             )}
          </div>

          <div className="space-y-1">
              {projects.map((project: any) => (
                  <ProjectTreeItem key={project.id} project={project} collapsed={collapsed} />
              ))}
              {projects.length === 0 && !collapsed && (
                  <div className="text-sm text-slate-600 px-4">No projects loaded</div>
              )}
          </div>

        </div>
      </ScrollArea>

      <div className="p-2 border-t border-white/10">
         <Button variant="ghost" size="icon" className="w-full h-10 hover:bg-white/5" onClick={() => setCollapsed(!collapsed)}>
             <LayoutGrid className={cn("transition-transform", collapsed ? "rotate-180" : "")} size={18} />
         </Button>
      </div>
    </aside>
  );
}
