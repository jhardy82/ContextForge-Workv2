
import { useListActionListsApiV1ActionListsGet } from '@/api/generated/action-lists/action-lists';
import { useListProjectsApiV1ProjectsGet } from '@/api/generated/projects/projects';
import { useListSprintsApiV1SprintsGet } from '@/api/generated/sprints/sprints';
import { useListTasksApiV1TasksGet } from '@/api/generated/tasks/tasks';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger,
} from '@/components/ui/tabs';
import {
    Database,
    Download,
    FileJson,
    Search
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

export function DataExplorer() {
  console.debug('[DEBUG] DataExplorer rendering');
  const [searchTerm, setSearchTerm] = useState('');
  const [showRawJson, setShowRawJson] = useState(false);

  // Fetch all data entities using Orval hooks
  const { data: taskList, isLoading: isLoadingTasks } = useListTasksApiV1TasksGet();
  const { data: projectList, isLoading: isLoadingProjects } = useListProjectsApiV1ProjectsGet();
  const { data: sprintList, isLoading: isLoadingSprints } = useListSprintsApiV1SprintsGet();
  const { data: actionListCollection, isLoading: isLoadingActionLists } = useListActionListsApiV1ActionListsGet();

  // Map to arrays for compatibility
  const tasks = useMemo(() => (taskList?.tasks || []) as any[], [taskList]);
  const projects = useMemo(() => (projectList?.projects || []) as any[], [projectList]);
  const sprints = useMemo(() => (sprintList?.sprints || []) as any[], [sprintList]);
  const actionLists = useMemo(() => (actionListCollection?.action_lists || []) as any[], [actionListCollection]);

  const filterData = (data: any[]) => {
    if (!searchTerm) return data;
    const lowerTerm = searchTerm.toLowerCase();
    return data.filter(item =>
      JSON.stringify(item).toLowerCase().includes(lowerTerm)
    );
  };

  const handleExport = (data: any[], filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}-${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success(`Exported ${filename}`);
  };

  const RenderTable = ({ data, columns, type }: { data: any[], columns: string[], type: string }) => {
    const filtered = filterData(data);

    if (showRawJson) {
      return (
        <ScrollArea className="h-[600px] w-full rounded-md border p-4 bg-slate-950 text-slate-50 font-mono text-xs">
          <pre>{JSON.stringify(filtered, null, 2)}</pre>
        </ScrollArea>
      );
    }

    return (
      <div className="rounded-md border border-white/10 overflow-hidden">
        <ScrollArea className="h-[600px]">
          <Table>
            <TableHeader className="bg-slate-900/50">
              <TableRow className="hover:bg-transparent border-white/10">
                {columns.map(col => (
                  <TableHead key={col} className="text-slate-400 font-medium capitalize">
                    {col.replace(/_/g, ' ')}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((row: any, i: number) => (
                <TableRow key={row.id || i} className="hover:bg-white/5 border-white/10">
                  {columns.map(col => (
                    <TableCell key={`${row.id}-${col}`} className="text-slate-300">
                      {typeof row[col] === 'object' ? (
                        <span className="text-xs text-slate-500 font-mono">
                          {JSON.stringify(row[col]).slice(0, 30)}...
                        </span>
                      ) : (
                        String(row[col] || '-')
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </ScrollArea>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Database className="w-6 h-6 text-cyan-400" />
            Data Explorer
          </h2>
          <p className="text-muted-foreground">
            Inspect, search, and export raw database entities.
          </p>
        </div>
        <div className="flex items-center gap-2">
           <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRawJson(!showRawJson)}
            className={showRawJson ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/50" : ""}
          >
            <FileJson className="w-4 h-4 mr-2" />
            {showRawJson ? 'View Table' : 'View JSON'}
          </Button>
        </div>
      </div>

      <Card className="glass border-white/10">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-medium text-slate-200">Database Entities</CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative w-64">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search all fields..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 bg-slate-950/50 border-white/10 focus:border-cyan-500/50"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="tasks" className="w-full">
            <div className="flex items-center justify-between mb-4">
                <TabsList className="bg-slate-950/50 border border-white/10">
                <TabsTrigger value="tasks" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-300">
                    Tasks <Badge variant="secondary" className="ml-2 text-[10px]">{tasks.length}</Badge>
                </TabsTrigger>
                <TabsTrigger value="projects" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                    Projects <Badge variant="secondary" className="ml-2 text-[10px]">{projects.length}</Badge>
                </TabsTrigger>
                <TabsTrigger value="sprints" className="data-[state=active]:bg-blue-500/20 data-[state=active]:text-blue-300">
                    Sprints <Badge variant="secondary" className="ml-2 text-[10px]">{sprints.length}</Badge>
                </TabsTrigger>
                <TabsTrigger value="action_lists" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-300">
                    Action Lists <Badge variant="secondary" className="ml-2 text-[10px]">{actionLists.length}</Badge>
                </TabsTrigger>
                </TabsList>

                <Button variant="outline" size="sm" onClick={() => {
                    const activeTab = document.querySelector('[role="tab"][data-state="active"]')?.textContent?.split(' ')[0].toLowerCase();
                    if(activeTab?.includes('task')) handleExport(tasks, 'tasks');
                    if(activeTab?.includes('project')) handleExport(projects, 'projects');
                    if(activeTab?.includes('sprint')) handleExport(sprints, 'sprints');
                    if(activeTab?.includes('action')) handleExport(actionLists, 'action_lists');
                }}>
                    <Download className="w-4 h-4 mr-2" />
                    Export Current View
                </Button>
            </div>

            <TabsContent value="tasks" className="mt-0">
              <RenderTable
                data={tasks}
                columns={['title', 'status', 'priority', 'project_id', 'created_at', 'updated_at']}
                type="tasks"
              />
            </TabsContent>

            <TabsContent value="projects" className="mt-0">
              <RenderTable
                data={projects}
                columns={['name', 'status', 'description', 'created_at']}
                type="projects"
              />
            </TabsContent>

            <TabsContent value="sprints" className="mt-0">
               <RenderTable
                data={sprints}
                columns={['name', 'status', 'start_date', 'end_date', 'project_id']}
                type="sprints"
              />
            </TabsContent>

            <TabsContent value="action_lists" className="mt-0">
               <RenderTable
                data={actionLists}
                columns={['title', 'project_id', 'created_at', 'updated_at']}
                type="action_lists"
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
