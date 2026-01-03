import { useCreateSprintApiV1SprintsPost, useListSprintsApiV1SprintsGet, useUpdateSprintApiV1SprintsSprintIdPut } from "@/api/generated/sprints/sprints";
import { useListTasksApiV1TasksGet, useUpdateTaskApiV1TasksTaskIdPut } from "@/api/generated/tasks/tasks";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Sprint, Task } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Calendar, ChevronRight, Plus, Timer } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { VelocityChart } from "./VelocityChart";

export function SprintView() {
  const queryClient = useQueryClient();
  const [selectedSprint, setSelectedSprint] = useState<string | null>(null);

  // Queries
  const { data: sprintList } = useListSprintsApiV1SprintsGet();
  const sprints = (sprintList?.sprints || []).map((s: any) => ({
      ...s,
      project_id: s.primary_project // Match legacy interface
  })) as Sprint[];

  const { data: taskList } = useListTasksApiV1TasksGet();
  const tasks = (taskList?.tasks || []).map((t: any) => ({
      ...t,
      project_id: t.primary_project,
      sprint_id: t.primary_sprint,
      due_date: t.due_at,
      priority: t.priority // Ensure priority matches
  })) as Task[];

  // Mutations
  const createSprintMutationGenerated = useCreateSprintApiV1SprintsPost();
  const updateSprintMutationGenerated = useUpdateSprintApiV1SprintsSprintIdPut();
  const updateTaskMutationGenerated = useUpdateTaskApiV1TasksTaskIdPut();

  const createSprintMutation = useMutation({
    mutationFn: (sprint: Partial<Sprint>) => {
        const payload = {
            ...sprint,
            primary_project: sprint.project_id || 'default',
            status: 'planned',
            cadence: "2_weeks", // Default required field
            owner: "user"       // Default required field
        };
        return createSprintMutationGenerated.mutateAsync({ data: payload as any });
    },
    onSuccess: () => {
      // Invalidate specific query key if possible, or just refetch
      queryClient.invalidateQueries({ queryKey: ['/api/v1/sprints'] });
      toast.success("Sprint created successfully");
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, updates }: { taskId: string; updates: Partial<Task> }) => {
       // Map updates if necessary
       const payload = { ...updates };
       if (updates.sprint_id) {
           (payload as any).primary_sprint = updates.sprint_id;
       }
       return updateTaskMutationGenerated.mutateAsync({ taskId, data: payload as any });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks'] });
      toast.success("Task updated");
    },
  });

  // Derived state
  const backlogTasks = tasks.filter(t => !t.sprint_id && t.status !== 'done' && t.status !== 'cancelled');
  const activeSprints = sprints.filter(s => s.status === 'active');
  const plannedSprints = sprints.filter(s => s.status === 'planned');

  const handleCreateSprint = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    createSprintMutation.mutate({
      name: formData.get('name') as string,
      start_date: new Date().toISOString(),
      end_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(), // 2 weeks default
      status: 'planned',
      project_id: 'default', // TODO: Add project selector
    });
  };

  const updateSprintMutation = useMutation({
    mutationFn: ({ sprintId, updates }: { sprintId: string; updates: Partial<Sprint> }) =>
      updateSprintMutationGenerated.mutateAsync({ sprintId, data: updates as any }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/v1/sprints'] });
      toast.success("Sprint updated");
    },
  });

  const handleUpdateSprintGoal = (sprintId: string, goal: string) => {
    updateSprintMutation.mutate({ sprintId, updates: { goal } });
  };

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId);
  };

  const handleDrop = (e: React.DragEvent, sprintId: string) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    if (taskId) {
      updateTaskMutation.mutate({ taskId, updates: { sprint_id: sprintId } });
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
      {/* Backlog Column */}
      <Card className="col-span-1 flex flex-col h-full glass border-0">
        <CardHeader className="pb-3 border-b border-white/5 bg-white/5">
          <CardTitle className="text-sm font-medium flex items-center justify-between text-white/90">
            <span>Backlog</span>
            <Badge variant="secondary" className="bg-white/10 text-white hover:bg-white/20">{backlogTasks.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea className="h-full px-4 pb-4">
            <div className="space-y-2 pt-4">
              {backlogTasks.map(task => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, task.id)}
                  className="p-3 glass-card rounded-md cursor-move hover:border-cyan-400/50 transition-all group neon-border"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-sm font-medium line-clamp-2 text-white/80 group-hover:text-cyan-400 transition-colors">{task.title}</span>
                    <Badge variant={task.priority === 'high' || task.priority === 'critical' ? 'destructive' : 'outline'} className="text-[10px] px-1 py-0 h-5 border-white/10">
                      {task.priority}
                    </Badge>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground group-hover:text-cyan-400/60 transition-colors">
                    <Badge variant="secondary" className="text-[10px] px-1 h-4 font-normal bg-white/5 text-muted-foreground">{task.id.slice(0, 6)}</Badge>
                    {task.estimated_hours && (
                      <span className="flex items-center gap-1">
                        <Timer className="w-3 h-3" /> {task.estimated_hours}h
                      </span>
                    )}
                  </div>
                </div>
              ))}
              {backlogTasks.length === 0 && (
                <div className="text-center py-8 text-sm text-muted-foreground italic">
                  No unassigned tasks
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Sprints Column */}
      <div className="col-span-1 md:col-span-2 space-y-6 overflow-y-auto pr-2 pb-10">

        {/* Velocity Chart */}
        <VelocityChart />

        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold tracking-tight">Active Sprints</h2>
          <Dialog>
            <DialogTrigger asChild>
              <Button size="sm" className="bg-cyan-500 hover:bg-cyan-600 text-white border-0"><Plus className="w-4 h-4 mr-1" /> New Sprint</Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-900 border-white/10 text-white">
              <DialogHeader>
                <DialogTitle>Create New Sprint</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateSprint} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="name" className="text-sm font-medium">Sprint Name</label>
                  <Input id="name" name="name" placeholder="Sprint 24" required className="bg-white/5 border-white/10" />
                </div>
                <Button type="submit" className="w-full bg-cyan-500 hover:bg-cyan-600">Create Sprint</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Active Sprints */}
        {activeSprints.map(sprint => (
          <SprintCard
            key={sprint.id}
            sprint={sprint}
            tasks={tasks.filter(t => t.sprint_id === sprint.id)}
            onDrop={handleDrop}
            onGoalChange={handleUpdateSprintGoal}
          />
        ))}

        {activeSprints.length === 0 && (
          <div className="p-8 border-2 border-dashed rounded-lg text-center text-muted-foreground">
            No active sprints
          </div>
        )}

        <Separator />

        <h2 className="text-lg font-semibold tracking-tight text-muted-foreground">Planned Sprints</h2>
         {plannedSprints.map(sprint => (
          <SprintCard
            key={sprint.id}
            sprint={sprint}
            tasks={tasks.filter(t => t.sprint_id === sprint.id)}
            onDrop={handleDrop}
            onGoalChange={handleUpdateSprintGoal}
          />
        ))}
      </div>
    </div>
  );
}

function SprintCard({ sprint, tasks, onDrop, onGoalChange }: { sprint: Sprint; tasks: Task[]; onDrop: (e: React.DragEvent, id: string) => void; onGoalChange: (id: string, goal: string) => void }) {
  return (
    <Card
      className={cn(
        "border-l-4 transition-all glass border-0",
        sprint.status === 'active' ? "border-l-cyan-400" : "border-l-purple-500"
      )}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => onDrop(e, sprint.id)}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center justify-between text-white/90">
          <div className="flex items-center gap-2">
            {sprint.name}
            <Badge variant={sprint.status === 'active' ? 'default' : 'secondary'} className={cn("text-xs uppercase", sprint.status === 'active' && "bg-cyan-500 hover:bg-cyan-600")}>
              {sprint.status}
            </Badge>
          </div>
          <div className="text-xs font-normal text-muted-foreground flex items-center gap-4">
            <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(sprint.start_date).toLocaleDateString()}</span>
            <span className="flex items-center gap-1"><ChevronRight className="w-3 h-3" /> {new Date(sprint.end_date).toLocaleDateString()}</span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
            {/* Sprint Goal */}
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Sprint Goal</label>
                <Input
                    defaultValue={sprint.goal || ""}
                    placeholder="Enter sprint goal..."
                    onBlur={(e) => onGoalChange(sprint.id, e.target.value)}
                    className="h-8 bg-white/5 border-transparent hover:border-white/10 focus:border-cyan-400 text-sm"
                />
            </div>

          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
            <span>{tasks.length} tasks</span>
            <span>{tasks.filter(t => t.status === 'done').length} completed</span>
          </div>
          {/* Progress Bar */}
          <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
            <div
              className={cn("h-full transition-all duration-500", sprint.status === 'active' ? "bg-cyan-400" : "bg-purple-500")}
              style={{ width: `${tasks.length ? (tasks.filter(t => t.status === 'done').length / tasks.length) * 100 : 0}%` }}
            />
          </div>

          {/* Task Preview (Collapsed) */}
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {tasks.map(task => (
               <div key={task.id} className="text-xs p-2 bg-white/5 rounded border border-white/5 flex items-center justify-between truncate hover:border-white/20 transition-colors">
                 <span className={cn("truncate text-white/70", task.status === 'done' && "line-through text-muted-foreground")}>{task.title}</span>
                 <div className={cn("w-2 h-2 rounded-full flex-shrink-0 ml-2 shadow-[0_0_5px_rgba(0,0,0,0.5)]",
                   task.status === 'done' ? 'bg-green-500' :
                   task.status === 'in_progress' ? 'bg-cyan-400' : 'bg-white/20'
                 )} />
               </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
