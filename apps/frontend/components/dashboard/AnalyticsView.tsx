import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Task } from "@/lib/types";
import { motion } from "framer-motion";
import { Activity, CheckCircle2, TrendingUp, Zap } from "lucide-react";
import { useMemo } from "react";
import {
    Area,
    AreaChart,
    Cell,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip
} from "recharts";

import { Project } from "@/lib/types";

interface AnalyticsViewProps {
  tasks: Task[];
  projects?: Project[];
}

export function AnalyticsView({ tasks, projects = [] }: AnalyticsViewProps) {
  // 1. Velocity Aura Data (Real Calculation)
  const velocityData = useMemo(() => {
    // Group completed tasks by day (last 7 days)
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const data = new Array(7).fill(0).map((_, i) => {
        const d = new Date();
        d.setDate(d.getDate() - (6 - i));
        return {
            name: days[d.getDay()],
            date: d.toISOString().split('T')[0],
            velocity: 0
        };
    });

    tasks.forEach(t => {
        if (t.status === 'done' && t.updated_at) {
            const date = t.updated_at.split('T')[0];
            const point = data.find(d => d.date === date);
            if (point) point.velocity += (t.estimated_hours || 1); // Use estimated hours or 1 point
        }
    });

    return data;
  }, [tasks]);

  // 2. Task Distribution Data (Real)
  const distributionData = useMemo(() => {
    const counts = {
      todo: tasks.filter(t => t.status === 'todo').length,
      in_progress: tasks.filter(t => t.status === 'in_progress').length,
      done: tasks.filter(t => t.status === 'done').length,
      blocked: tasks.filter(t => t.status === 'blocked').length,
    };
    return [
      { name: "To Do", value: counts.todo, color: "#94a3b8" }, // Slate 400
      { name: "In Progress", value: counts.in_progress, color: "#3b82f6" }, // Blue 500
      { name: "Done", value: counts.done, color: "#22c55e" }, // Green 500
      { name: "Blocked", value: counts.blocked, color: "#ef4444" }, // Red 500
    ];
  }, [tasks]);

  // 3. Blockers Analysis (New Feature)
  const blockersCount = useMemo(() => tasks.filter(t => t.status === 'blocked').length, [tasks]);
  const activeProjectsCount = useMemo(() => projects.filter(p => p.status === 'active').length, [projects]);

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
          Analytics & Insights
        </h2>
        <p className="text-muted-foreground mt-1">
          Visualizing team performance through the lens of data art.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Velocity"
          value={String(velocityData.reduce((acc, curr) => acc + curr.velocity, 0))}
          icon={<Zap className="w-4 h-4 text-yellow-400" />}
          description="Points last 7 days"
          delay={0.1}
        />
        <StatCard
            title="Completion Rate"
            value={`${tasks.length ? Math.round((tasks.filter(t => t.status === 'done').length / tasks.length) * 100) : 0}%`}
            icon={<CheckCircle2 className="w-4 h-4 text-green-400" />}
            description="Tasks completed"
            delay={0.2}
        />
        <StatCard
            title="Blocked Tasks"
            value={String(blockersCount)}
            icon={<Activity className="w-4 h-4 text-red-500" />}
            description="Critical bottlenecks"
            delay={0.3}
        />
         <StatCard
            title="Active Projects"
            value={String(activeProjectsCount)}
             icon={<TrendingUp className="w-4 h-4 text-purple-400" />}
            description="Workstreams"
            delay={0.4}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Velocity Aura Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="border-0 bg-gradient-to-br from-slate-900/50 to-slate-800/50 backdrop-blur-xl shadow-xl overflow-hidden relative">
            <div className="absolute inset-0 bg-blue-500/10 blur-3xl rounded-full -top-1/2 -left-1/2 pointer-events-none" />
            <CardHeader>
              <CardTitle className="text-white/90">Velocity Aura</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={velocityData}>
                  <defs>
                    <linearGradient id="colorVelocity" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px', color: '#fff' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="velocity"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorVelocity)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Task Distribution (Donut) */}
         <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="border-0 bg-gradient-to-bl from-slate-900/50 to-slate-800/50 backdrop-blur-xl shadow-xl overflow-hidden relative">
             <div className="absolute inset-0 bg-purple-500/10 blur-3xl rounded-full -bottom-1/2 -right-1/2 pointer-events-none" />
            <CardHeader>
              <CardTitle className="text-white/90">Task Distribution</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={distributionData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {distributionData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                            ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px', color: '#fff' }} />
                    </PieChart>
                </ResponsiveContainer>
                {/* Legend */}
                 <div className="flex justify-center gap-4 mt-[-20px] relative z-10">
                    {distributionData.map((entry) => (
                        <div key={entry.name} className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                            <span className="text-xs text-muted-foreground">{entry.name}</span>
                        </div>
                    ))}
                </div>
            </CardContent>
          </Card>
        </motion.div>

         {/* Blockers Analysis (Replaces Rhythm for now) */}
         <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="col-span-1 lg:col-span-2"
        >
          <Card className="border-0 bg-gradient-to-r from-red-900/10 to-transparent backdrop-blur-xl shadow-xl overflow-hidden relative border-l-4 border-l-red-500/50">
            <CardHeader>
                <CardTitle className="text-white/90">Bottleneck Radar</CardTitle>
            </CardHeader>
             <CardContent>
                 <div className="space-y-4">
                    {tasks.filter(t => t.status === 'blocked').slice(0, 5).map(task => (
                        <div key={task.id} className="flex items-center justify-between p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                            <span className="text-sm font-medium text-red-200">{task.title}</span>
                             <span className="text-xs text-red-300 bg-red-500/20 px-2 py-1 rounded">
                                 {task.priority.toUpperCase()}
                             </span>
                        </div>
                    ))}
                    {blockersCount === 0 && (
                        <p className="text-emerald-400 text-sm flex items-center gap-2">
                            <CheckCircle2 size={16} /> No bottlenecks detected. System healthy.
                        </p>
                    )}
                 </div>
             </CardContent>
          </Card>
         </motion.div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, description, delay }: { title: string; value: string; icon: React.ReactNode; description: string; delay: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay }}
        >
            <Card className="bg-slate-900/40 border-slate-800/50 backdrop-blur-sm">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between space-y-0 pb-2">
                        <span className="text-sm font-medium text-muted-foreground">{title}</span>
                        {icon}
                    </div>
                    <div className="text-2xl font-bold text-white">{value}</div>
                    <p className="text-xs text-muted-foreground mt-1">{description}</p>
                </CardContent>
            </Card>
        </motion.div>
    )
}
