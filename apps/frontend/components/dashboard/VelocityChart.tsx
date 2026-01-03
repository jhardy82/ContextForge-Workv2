
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Mock data generator (since API might not return historical velocity yet)
const generateVelocityData = () => [
  { name: 'Sprint 20', points: 24, completed: 22 },
  { name: 'Sprint 21', points: 30, completed: 28 },
  { name: 'Sprint 22', points: 28, completed: 25 },
  { name: 'Sprint 23', points: 32, completed: 30 },
  { name: 'Sprint 24', points: 35, completed: 15 }, // Current
];

export function VelocityChart() {
  const data = generateVelocityData();

  return (
    <Card className="glass border-0 h-64">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">Team Velocity</CardTitle>
      </CardHeader>
      <CardContent className="h-[calc(100%-60px)] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <XAxis
                dataKey="name"
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
            />
            <YAxis
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `${value}pts`}
            />
            <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
            />
            <Bar dataKey="completed" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            <Bar dataKey="points" fill="rgba(255,255,255,0.1)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
