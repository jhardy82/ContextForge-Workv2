import { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Power, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ConnectionStatus from './connection-status';
import TaskTree from './task-tree';
import TaskDetailModal from './task-detail-modal';
import { Logo } from '@/components/theme/logo';
import { SettingsModal } from '@/components/theme/settings-modal';
import { DTMApiClient } from '@/lib/dtm-api';
import { Project, Task, ConnectionStatus as ConnectionStatusType } from '@/lib/types';
import { useKV } from '@github/spark/hooks';

const DEFAULT_API_URL = 'http://localhost:3000/api';
const REFRESH_INTERVAL = 30000; // 30 seconds

export default function DTMDashboard() {
  const [apiClient] = useState(() => new DTMApiClient(DEFAULT_API_URL));
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatusType>({
    connected: false,
    status: 'disconnected'
  });
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCheckingServers, setIsCheckingServers] = useState(false);
  const [serverCheckResult, setServerCheckResult] = useState<any>(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useKV('dtm-auto-refresh', 'true');

  const checkConnection = useCallback(async () => {
    const status = await apiClient.checkHealth();
    setConnectionStatus(status);
    return status.connected;
  }, [apiClient]);

  // Browser-compatible server health check (replaces Node.js activation)
  const handleServerCheck = useCallback(async () => {
    setIsCheckingServers(true);
    try {
      // Check DTM API server health
      const dtmController = new AbortController();
      const dtmTimeout = setTimeout(() => dtmController.abort(), 5000);
      const dtmHealthy = await fetch('http://localhost:3000/api/health', {
        method: 'GET',
        signal: dtmController.signal
      }).then(res => res.ok).catch(() => false).finally(() => clearTimeout(dtmTimeout));

      // Check TaskMan-v2 dev server (if different port)
      const taskManController = new AbortController();
      const taskManTimeout = setTimeout(() => taskManController.abort(), 5000);
      const taskManHealthy = await fetch('http://localhost:5000/', {
        method: 'GET',
        signal: taskManController.signal
      }).then(res => res.ok).catch(() => false).finally(() => clearTimeout(taskManTimeout));

      const result = {
        success: dtmHealthy || taskManHealthy,
        dtmServerRunning: dtmHealthy,
        taskManV2Running: taskManHealthy,
        message: dtmHealthy && taskManHealthy
          ? 'All servers are running'
          : dtmHealthy
            ? 'DTM server running, TaskMan-v2 needs to be started manually'
            : taskManHealthy
              ? 'TaskMan-v2 running, DTM server needs to be started manually'
              : 'Servers need to be started manually - this web app cannot start servers',
        errors: []
      };

      setServerCheckResult(result);

      // Refresh connection status after check
      setTimeout(() => {
        handleRefresh();
      }, 1000);
    } catch (error) {
      console.error('Server check failed:', error);
      setServerCheckResult({
        success: false,
        dtmServerRunning: false,
        taskManV2Running: false,
        message: 'Server check failed',
        errors: [error instanceof Error ? error.message : 'Unknown error']
      });
    } finally {
      setIsCheckingServers(false);
    }
  }, []);

  const loadData = useCallback(async () => {
    try {
      const [projectsData, tasksData] = await Promise.all([
        apiClient.getProjects(),
        apiClient.getTasks()
      ]);

      setProjects(projectsData);
      setTasks(tasksData);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  }, [apiClient]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const isConnected = await checkConnection();
      if (isConnected || !apiClient.isConnected()) {
        await loadData();
      }
    } finally {
      setIsRefreshing(false);
    }
  }, [checkConnection, loadData, apiClient]);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsDetailModalOpen(true);
  };

  const handleCloseDetailModal = () => {
    setIsDetailModalOpen(false);
    setSelectedTask(null);
  };

  // Initial load with auto-activation
  useEffect(() => {
    const initializeSystem = async () => {
      // First check if DTM server is already running
      const isConnected = await checkConnection();

      if (!isConnected) {
        // Check server status instead of trying to activate
        await handleServerCheck();
      } else {
        // Server is already running, just load data
        await handleRefresh();
      }
    };

    initializeSystem();
  }, []);

  // Auto-refresh
  useEffect(() => {
    if (autoRefreshEnabled !== 'true') return;

    const interval = setInterval(() => {
      handleRefresh();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [autoRefreshEnabled, handleRefresh]);

  // Calculate statistics
  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    totalTasks: tasks.length,
    completedTasks: tasks.filter(t => t.status === 'completed').length,
    inProgressTasks: tasks.filter(t => t.status === 'in_progress').length,
    pendingTasks: tasks.filter(t => t.status === 'pending').length,
    blockedTasks: tasks.filter(t => t.status === 'blocked').length
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-6 px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Logo />

          <div className="flex items-center gap-2">
            <SettingsModal />

            {!connectionStatus.connected && (
              <Button
                variant="default"
                size="sm"
                onClick={handleServerCheck}
                disabled={isCheckingServers}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isCheckingServers ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Power className="h-4 w-4 mr-2" />
                )}
                {isCheckingServers ? 'Checking Servers...' : 'Check Servers'}
              </Button>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoRefreshEnabled(autoRefreshEnabled === 'true' ? 'false' : 'true')}
              className={autoRefreshEnabled === 'true' ? "bg-primary/10" : ""}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${autoRefreshEnabled === 'true' ? 'animate-spin' : ''}`} />
              Auto-refresh {autoRefreshEnabled === 'true' ? 'ON' : 'OFF'}
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              {isRefreshing ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
          </div>
        </div>

        {/* Connection Status */}
        <ConnectionStatus
          status={connectionStatus}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />

        {/* Server Check Status */}
        {serverCheckResult && (
          <Alert className={`mb-4 ${serverCheckResult.success ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
            <AlertTriangle className={`h-4 w-4 ${serverCheckResult.success ? 'text-green-600' : 'text-yellow-600'}`} />
            <AlertDescription className={serverCheckResult.success ? 'text-green-800' : 'text-yellow-800'}>
              <div className="font-medium">{serverCheckResult.message}</div>
              {serverCheckResult.errors && serverCheckResult.errors.length > 0 && (
                <ul className="mt-2 text-sm list-disc list-inside">
                  {serverCheckResult.errors.map((error: string, index: number) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              )}
              <div className="mt-2 text-sm">
                DTM Server: {serverCheckResult.dtmServerRunning ? '✅ Running' : '❌ Not Running'} |
                TaskMan-v2: {serverCheckResult.taskManV2Running ? '✅ Running' : '⚠️ Check Dev Server'}
              </div>
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Statistics Panel */}
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Projects</span>
                  <span className="font-medium">{stats.activeProjects}/{stats.totalProjects}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Total Tasks</span>
                  <span className="font-medium">{stats.totalTasks}</span>
                </div>
                <div className="h-px bg-border" />
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-status-completed">Completed</span>
                    <span className="font-medium">{stats.completedTasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-status-in-progress">In Progress</span>
                    <span className="font-medium">{stats.inProgressTasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-status-pending">Pending</span>
                    <span className="font-medium">{stats.pendingTasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-status-blocked">Blocked</span>
                    <span className="font-medium">{stats.blockedTasks}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Info */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">
                  Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div>
                  <span className="text-muted-foreground">API URL:</span>
                  <div className="font-mono text-xs mt-1 p-2 bg-muted rounded">
                    {DEFAULT_API_URL}
                  </div>
                </div>
                <div>
                  <span className="text-muted-foreground">Refresh Interval:</span>
                  <div className="text-xs">{REFRESH_INTERVAL / 1000}s</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Mode:</span>
                  <div className="text-xs">
                    {connectionStatus.connected ? 'Live API' : 'Sample Data'}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Task Tree */}
          <div className="lg:col-span-3">
            <Card className="h-[600px]">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Project & Task Hierarchy</CardTitle>
              </CardHeader>
              <CardContent className="p-0 h-full overflow-hidden">
                <div className="h-full overflow-y-auto">
                  <TaskTree
                    projects={projects}
                    tasks={tasks}
                    onTaskClick={handleTaskClick}
                    selectedTaskId={selectedTask?.id}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Task Detail Modal */}
        <TaskDetailModal
          task={selectedTask}
          isOpen={isDetailModalOpen}
          onClose={handleCloseDetailModal}
          apiClient={apiClient}
        />
      </div>
    </div>
  );
}
