
import { useListTasksApiV1TasksGet } from '@/api/generated/tasks/tasks';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { addDays, differenceInDays, format, isAfter, isBefore, isValid, parseISO, startOfDay } from 'date-fns';
import { Search } from 'lucide-react';
import { useMemo, useState } from 'react';

export function TimelineView() {
  console.debug('[DEBUG] TimelineView rendering');
  const [zoomLevel, setZoomLevel] = useState<'week' | 'month'>('month');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch tasks using generated Orval hook
  const { data: taskList } = useListTasksApiV1TasksGet();

  // Map to array for compatibility
  const tasks = useMemo(() => {
    console.debug('[DEBUG] TimelineView mapping tasks:', taskList?.tasks?.length || 0);
    return (taskList?.tasks || []) as any[];
  }, [taskList]);


  // Calculate timeline range
  const { startDate, endDate, days } = useMemo(() => {
    // Default to current month +/- 15 days if no tasks
    const today = startOfDay(new Date());
    let start = addDays(today, -7);
    let end = addDays(today, 21);

    const validTasks = tasks.filter(t => t.created_at || t.due_date);

    if (validTasks.length > 0) {
      // Find min start date and max end date
      const dates = validTasks.flatMap(t => {
        const d = [];
        if (t.created_at) d.push(parseISO(t.created_at));
        if (t.due_date) d.push(parseISO(t.due_date));
        return d;
      }).filter(isValid);

      if (dates.length > 0) {
        start = dates.reduce((a, b) => isBefore(a, b) ? a : b);
        end = dates.reduce((a, b) => isAfter(a, b) ? a : b);

        // Add padding
        start = addDays(start, -3);
        end = addDays(end, 7);
      }
    }

    const dayCount = differenceInDays(end, start) + 1;
    const dayArray = Array.from({ length: dayCount }, (_, i) => addDays(start, i));

    return { startDate: start, endDate: end, days: dayArray };
  }, [tasks]);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase());
      const hasDates = task.created_at || task.due_date;
      return matchesSearch && hasDates;
    }).sort((a, b) => {
        const dateA = a.created_at ? parseISO(a.created_at) : new Date(0);
        const dateB = b.created_at ? parseISO(b.created_at) : new Date(0);
        return dateA.getTime() - dateB.getTime();
    });
  }, [tasks, searchQuery]);

  // Grid sizing
  const COLUMN_WIDTH = 50;
  const ROW_HEIGHT = 48;
  const HEADER_HEIGHT = 40;

  return (
    <div className="h-full flex flex-col space-y-4">
        {/* Toolbar */}
        <div className="flex items-center justify-between p-1">
            <div className="flex items-center space-x-2">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Filter tasks..."
                        className="pl-9 pr-4 py-2 rounded-lg bg-black/20 border border-white/10 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
            </div>
            <div className="flex items-center space-x-2 bg-black/20 rounded-lg p-1 border border-white/10">
                <button
                    onClick={() => setZoomLevel('week')}
                    className={`px-3 py-1.5 rounded-md text-sm transition-colors ${zoomLevel === 'week' ? 'bg-cyan-500/20 text-cyan-300' : 'text-muted-foreground hover:text-white'}`}
                >
                    Week
                </button>
                <button
                    onClick={() => setZoomLevel('month')}
                    className={`px-3 py-1.5 rounded-md text-sm transition-colors ${zoomLevel === 'month' ? 'bg-purple-500/20 text-purple-300' : 'text-muted-foreground hover:text-white'}`}
                >
                    Month
                </button>
            </div>
        </div>

        {/* Timeline Container */}
        <Card className="flex-1 overflow-hidden glass border-0 bg-black/20">
            <CardContent className="p-0 h-full overflow-auto relative">
                <div style={{ minWidth: days.length * COLUMN_WIDTH + 300, height: '100%' }}>

                    {/* Header Row */}
                    <div className="sticky top-0 z-10 flex border-b border-white/10 bg-black/40 backdrop-blur-xl h-[40px]">
                        <div className="w-[300px] sticky left-0 z-20 bg-black/40 border-r border-white/10 flex items-center px-4 font-semibold text-sm">
                            Task Name
                        </div>
                        <div className="flex">
                            {days.map((day) => (
                                <div
                                    key={day.toISOString()}
                                    className="border-r border-white/5 flex flex-col items-center justify-center text-xs text-muted-foreground"
                                    style={{ width: COLUMN_WIDTH }}
                                >
                                    <span className="font-medium">{format(day, 'd')}</span>
                                    <span className="text-[10px] opacity-70">{format(day, 'EE')}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Task Rows */}
                    <div className="relative">
                        {/* Vertical Grid Lines */}
                         <div className="absolute inset-0 flex left-[300px] pointer-events-none" style={{ width: days.length * COLUMN_WIDTH }}>
                            {days.map((day) => (
                                <div
                                    key={`grid-${day.toISOString()}`}
                                    className={`h-full border-r border-white/5 ${[0, 6].includes(day.getDay()) ? 'bg-white/[0.02]' : ''}`}
                                    style={{ width: COLUMN_WIDTH }}
                                />
                            ))}
                        </div>

                        {filteredTasks.map((task) => {
                            // Calculate position
                            let taskStart = task.created_at ? parseISO(task.created_at) : startDate;
                            const taskEnd = task.due_date ? parseISO(task.due_date) : (taskStart ? addDays(taskStart, 1) : addDays(startDate, 1));

                            // Bounds check
                            if (isBefore(taskStart, startDate)) taskStart = startDate;

                            const offsetDays = differenceInDays(taskStart, startDate);
                            const durationDays = Math.max(1, differenceInDays(taskEnd, taskStart) + 1);

                            const left = offsetDays * COLUMN_WIDTH;
                            const width = durationDays * COLUMN_WIDTH;

                            // Status Colors
                            const statusColor =
                                task.status === 'done' ? 'bg-green-500/50 border-green-400' :
                                task.status === 'in_progress' ? 'bg-cyan-500/50 border-cyan-400' :
                                task.status === 'blocked' ? 'bg-red-500/50 border-red-400' :
                                'bg-slate-500/50 border-slate-400';

                            return (
                                <div key={task.id} className="group flex border-b border-white/5 hover:bg-white/5 transition-colors h-[48px]">
                                    {/* Task Info Column */}
                                    <div className="w-[300px] sticky left-0 z-10 bg-black/20 group-hover:bg-black/40 border-r border-white/10 flex items-center px-4 gap-3 transition-colors">
                                        <div className={`w-2 h-2 rounded-full ${
                                            task.priority === 'high' ? 'bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.5)]' :
                                            task.priority === 'medium' ? 'bg-yellow-400' : 'bg-blue-400'
                                        }`} />
                                        <div className="truncate text-sm font-medium">{task.title}</div>
                                        {task.status === 'done' && <Badge variant="outline" className="ml-auto text-xs h-5 border-green-500/50 text-green-400">Done</Badge>}
                                    </div>

                                    {/* Gantt Bar Area */}
                                    <div className="relative flex-1">
                                        {/* Grid lines are handled by absolute overlay above */}

                                        {/* Task Bar */}
                                        <div
                                            className={`absolute top-2.5 h-7 rounded-md border text-xs text-white px-2 flex items-center truncate shadow-lg cursor-pointer hover:brightness-110 transition-all ${statusColor}`}
                                            style={{
                                                left: left + 2, // +2 for padding
                                                width: width - 4 // -4 for padding
                                            }}
                                            title={`${task.title} (${format(taskStart, 'MMM d')} - ${format(taskEnd, 'MMM d')})`}
                                        >
                                            {width > 40 && <span className="drop-shadow-md truncate">{task.title}</span>}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}

                        {filteredTasks.length === 0 && (
                            <div className="py-12 text-center text-muted-foreground">
                                No tasks found matching your filters.
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    </div>
  );
}
