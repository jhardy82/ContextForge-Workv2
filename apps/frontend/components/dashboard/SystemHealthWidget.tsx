import { useQSEEvaluations, useQSEGates } from '@/api/features/useQSE';
import { useHealthCheckHealthGet } from '@/api/generated/default/default';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, CheckCircle2, Database, ShieldCheck } from 'lucide-react';

export function SystemHealthWidget() {
  const { data: health, isLoading: healthLoading } = useHealthCheckHealthGet();
  const { gates, isLoading: gatesLoading } = useQSEGates(true); // Enabled gates
  const { evaluations, isLoading: evalsLoading } = useQSEEvaluations({ limit: 100 });

  const isDbConnected = health?.database?.connected ?? false;
  const dbLatency = health?.database?.latency_ms;

  const totalEvaluations = evaluations.length;
  const passedEvaluations = evaluations.filter(e => e.passed).length;
  const passRate = totalEvaluations > 0 ? Math.round((passedEvaluations / totalEvaluations) * 100) : 0;

  const activeGatesCount = gates.length;

  const isLoading = healthLoading || gatesLoading || evalsLoading;

  if (isLoading) {
    return (
      <Card className="glass border-0">
        <CardContent className="p-4 flex items-center justify-center min-h-[140px]">
          <Activity className="w-6 h-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass border-0 h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
           <Activity className="w-4 h-4" /> System Health
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0 space-y-4">
        {/* Database Status */}
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <span className="text-sm">Database</span>
            </div>
            <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">
                    {dbLatency ? `${Math.round(dbLatency)}ms` : '-'}
                </span>
                <Badge variant={isDbConnected ? "default" : "destructive"} className="h-5">
                    {isDbConnected ? "Online" : "Offline"}
                </Badge>
            </div>
        </div>

        {/* QSE Status */}
        <div className="flex items-center justify-between">
             <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-purple-400" />
                <span className="text-sm">Quality Gates</span>
             </div>
             <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{activeGatesCount} Active</span>
             </div>
        </div>

        {/* Pass Rate */}
        <div className="flex items-center justify-between">
             <div className="flex items-center gap-2">
                <CheckCircle2 className={`w-4 h-4 ${passRate >= 80 ? 'text-green-400' : 'text-yellow-400'}`} />
                <span className="text-sm">Compliance</span>
             </div>
             <div className="flex items-center gap-2">
                <span className={`text-md font-bold ${passRate >= 80 ? 'text-green-400' : 'text-yellow-400'}`}>
                    {passRate}%
                </span>
             </div>
        </div>
      </CardContent>
    </Card>
  );
}
