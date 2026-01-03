import { Logo } from '@/components/theme/logo';
import { SettingsModal } from '@/components/theme/settings-modal';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Task2ApiClient } from '@/lib/task2-api';
import { ConnectionStatus as ConnectionStatusType, Project, Task } from '@/lib/types';
import { useKV } from '@github/spark/hooks';
import { AlertTriangle, Power, RefreshCw } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import ConnectionStatus from './connection-status';
import TaskDetailModal from './task-detail-modal';
import TaskTree from './task-tree';

const DEFAULT_API_URL = 'http://localhost:3001/api/v1';
const REFRESH_INTERVAL = 30000; // 30 seconds

export default function Task2Dashboard() {
  const [apiClient] = useState(() => new Task2ApiClient(DEFAULT_API_URL));
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
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useKV('task2-auto-refresh', 'true');

  const checkConnection = useCallback(async () => {
    const status = await apiClient.checkHealth();
    setConnectionStatus(status);
    return status.connected;
  }, [apiClient]);

  // Browser-compatible server health check (replaces Node.js activation)
  const handleServerCheck = useCallback(async () => {
    setIsCheckingServers(true);
    try {
      // Check TaskMan-v2 Backend API server health
      const task2Controller = new AbortController();
      const task2Timeout = setTimeout(() => task2Controller.abort(), 5000);
      const task2Healthy = await fetch('http://localhost:3001/api/v1/health', {
        method: 'GET',
        signal: task2Controller.signal
      }).then(res => res.ok).catch(() => false).finally(() => clearTimeout(task2Timeout));

      // Check TaskMan-v2 dev server (if different port)
      const taskManController = new AbortController();
      const taskManTimeout = setTimeout(() => taskManController.abort(), 5000);
      const taskManHealthy = await fetch('http://localhost:5000/', {
        method: 'GET',
        signal: taskManController.signal
      }).then(res => res.ok).catch(() => false).finally(() => clearTimeout(taskManTimeout));

      const result = {
        success: task2Healthy || taskManHealthy,
        task2ServerRunning: task2Healthy,
        taskManV2Running: taskManHealthy,
        message: task2Healthy && taskManHealthy
          ? 'All servers are running'
          : task2Healthy
            ? 'TaskMan-v2 Backend server running, TaskMan-v2 Frontend needs to be started manually'
            : taskManHealthy
              ? 'TaskMan-v2 Frontend running, TaskMan-v2 Backend server needs to be started manually'
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
        task2ServerRunning: false,
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
      // First check if TaskMan-v2 Backend server is already running
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
      if (connectionStatus.connected) {
        handleRefresh();
      }
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [connectionStatus.connected, handleRefresh, autoRefreshEnabled]);

  return (
    <>
      <div className="h-screen w-full bg-background relative">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="border-b bg-card">
            <div className="flex h-16 items-center justify-between px-6">
              <div className="flex items-center gap-3">
                <Logo className="w-8 h-8" />
                <div>
                  <h1 className="text-xl font-semibold">TaskMan-v2 (Task2) Dashboard</h1>
                  <p className="text-sm text-muted-foreground">
                    Advanced task management with Sacred Geometry integration
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleServerCheck}
                  disabled={isCheckingServers}
                  className="gap-2"
                >
                  <Power className="w-4 h-4" />
                  {isCheckingServers ? 'Checking...' : 'Check Servers'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  className="gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                  {isRefreshing ? 'Refreshing...' : 'Refresh'}
                </Button>
                <SettingsModal />
              </div>
            </div>
          </div>

          {/* Status Section */}
          <div className="p-6 border-b bg-muted/30">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Connection Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <ConnectionStatus
                    status={connectionStatus}
                    onRefresh={handleRefresh}
                    isRefreshing={isRefreshing}
                  />
                </CardContent>
              </Card>

              {serverCheckResult && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Server Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className={`flex items-center gap-2 text-sm ${
                        serverCheckResult.success ? 'text-green-600' : 'text-red-600'
                      }`}>
                        <div className={`w-2 h-2 rounded-full ${
                          serverCheckResult.success ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        {serverCheckResult.message}
                      </div>
                      <div className="text-xs text-muted-foreground space-y-1">
                        <div>TaskMan-v2 Backend: {serverCheckResult.task2ServerRunning ? '✅ Running' : '❌ Stopped'}</div>
                        <div>TaskMan-v2 Frontend: {serverCheckResult.taskManV2Running ? '✅ Running' : '❌ Stopped'}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {/* Alert for offline mode */}
          {!connectionStatus.connected && (
            <div className="p-6">
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  TaskMan-v2 Backend server is not available. Using offline mode with sample data.
                  Use the "Check Servers" button to verify server status.
                </AlertDescription>
              </Alert>
            </div>
          )}

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-hidden">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Task Management</CardTitle>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    {projects.length} project{projects.length !== 1 ? 's' : ''}, {tasks.length} task{tasks.length !== 1 ? 's' : ''}
                  </p>
                  {connectionStatus.connected && (
                    <div className="text-xs text-green-600">
                      🔄 Auto-refresh enabled
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="h-full overflow-hidden">
                <div className="h-full">
                  <TaskTree
                    projects={projects}
                    tasks={tasks}
                    onTaskClick={handleTaskClick}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Task Detail Modal */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={isDetailModalOpen}
        onClose={handleCloseDetailModal}
        apiClient={apiClient}
      />
    </>
  );
}
