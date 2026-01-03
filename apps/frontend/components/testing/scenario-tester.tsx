import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock,
  User,
  Desktop,
  Code,
  FileText,
  Plus,
  Trash,
  Eye
} from '@phosphor-icons/react';
import { toast } from 'sonner';

interface TestScenario {
  id: string;
  name: string;
  description: string;
  userStory: string;
  preconditions: string[];
  steps: ScenarioStep[];
  expectedOutcome: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  duration?: number;
  error?: string;
}

interface ScenarioStep {
  id: string;
  action: string;
  expected: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  details?: string;
}

export default function ScenarioTester() {
  const [scenarios, setScenarios] = useState<TestScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<TestScenario | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Initialize with predefined scenarios
  useEffect(() => {
    initializeScenarios();
  }, []);

  const initializeScenarios = () => {
    const defaultScenarios: TestScenario[] = [
      {
        id: 'developer-first-install',
        name: 'Developer First-Time Extension Install',
        description: 'A developer installs the DTM extension for the first time',
        userStory: 'As a developer, I want to install the Dynamic Task Manager extension from our GitHub app so that I can manage my development tasks directly in VS Code.',
        preconditions: [
          'VS Code is installed on the system',
          'Developer has access to the GitHub app',
          'Extension server is running and accessible',
          'Developer has internet connectivity'
        ],
        expectedOutcome: 'Developer successfully installs and uses the DTM extension to manage tasks',
        status: 'pending',
        steps: [
          {
            id: 'step-1',
            action: 'Developer visits the GitHub app URL',
            expected: 'GitHub app loads with extension server interface',
            status: 'pending'
          },
          {
            id: 'step-2',
            action: 'Developer clicks on "Dynamic Task Manager" extension',
            expected: 'Extension details and download options are displayed',
            status: 'pending'
          },
          {
            id: 'step-3',
            action: 'Developer downloads the .vsix file',
            expected: 'Extension file downloads successfully to local machine',
            status: 'pending'
          },
          {
            id: 'step-4',
            action: 'Developer runs installation command in VS Code',
            expected: 'Extension installs without errors',
            status: 'pending'
          },
          {
            id: 'step-5',
            action: 'Developer opens DTM extension in VS Code',
            expected: 'Extension UI loads and displays task management interface',
            status: 'pending'
          },
          {
            id: 'step-6',
            action: 'Developer creates a new task',
            expected: 'Task is created and visible in the task tree',
            status: 'pending'
          }
        ]
      },
      {
        id: 'team-collaboration',
        name: 'Team Collaboration Workflow',
        description: 'Multiple team members use the extension for collaborative task management',
        userStory: 'As a team lead, I want my team to use the same DTM extension so we can collaborate on project tasks efficiently.',
        preconditions: [
          'Multiple team members have VS Code installed',
          'All team members have access to the GitHub app',
          'DTM backend API is running and accessible',
          'Team has a shared project workspace'
        ],
        expectedOutcome: 'Team members can view, create, and update shared tasks collaboratively',
        status: 'pending',
        steps: [
          {
            id: 'collab-1',
            action: 'Team lead shares GitHub app URL with team',
            expected: 'All team members can access the extension server',
            status: 'pending'
          },
          {
            id: 'collab-2',
            action: 'Each team member installs the extension',
            expected: 'All installations complete successfully',
            status: 'pending'
          },
          {
            id: 'collab-3',
            action: 'Team lead creates project tasks',
            expected: 'Tasks are created and visible to team lead',
            status: 'pending'
          },
          {
            id: 'collab-4',
            action: 'Team members connect to shared DTM API',
            expected: 'All team members see the same task list',
            status: 'pending'
          },
          {
            id: 'collab-5',
            action: 'Team member updates task status',
            expected: 'Status update is visible to all team members',
            status: 'pending'
          },
          {
            id: 'collab-6',
            action: 'Team member adds comments to task',
            expected: 'Comments are synchronized across all instances',
            status: 'pending'
          }
        ]
      },
      {
        id: 'offline-online-sync',
        name: 'Offline/Online Synchronization',
        description: 'Extension handles offline work and syncs when connection is restored',
        userStory: 'As a developer who sometimes works offline, I want my task changes to sync automatically when I reconnect to the internet.',
        preconditions: [
          'DTM extension is installed and working',
          'Initial connection to DTM API is established',
          'Developer has some existing tasks'
        ],
        expectedOutcome: 'Offline changes sync successfully when connection is restored',
        status: 'pending',
        steps: [
          {
            id: 'sync-1',
            action: 'Developer works with stable internet connection',
            expected: 'All task operations work normally',
            status: 'pending'
          },
          {
            id: 'sync-2',
            action: 'Internet connection is lost',
            expected: 'Extension shows offline status indicator',
            status: 'pending'
          },
          {
            id: 'sync-3',
            action: 'Developer creates new tasks while offline',
            expected: 'Tasks are created locally and marked for sync',
            status: 'pending'
          },
          {
            id: 'sync-4',
            action: 'Developer modifies existing tasks while offline',
            expected: 'Changes are stored locally and marked for sync',
            status: 'pending'
          },
          {
            id: 'sync-5',
            action: 'Internet connection is restored',
            expected: 'Extension detects connection and begins sync process',
            status: 'pending'
          },
          {
            id: 'sync-6',
            action: 'Sync process completes',
            expected: 'All offline changes are synchronized with server',
            status: 'pending'
          }
        ]
      },
      {
        id: 'error-recovery',
        name: 'Error Handling and Recovery',
        description: 'Extension gracefully handles various error conditions',
        userStory: 'As a developer, I want the extension to handle errors gracefully and provide clear feedback when something goes wrong.',
        preconditions: [
          'DTM extension is installed',
          'Various error conditions can be simulated'
        ],
        expectedOutcome: 'Extension handles all error conditions gracefully with helpful user feedback',
        status: 'pending',
        steps: [
          {
            id: 'error-1',
            action: 'DTM API server becomes unavailable',
            expected: 'Extension shows connection error with retry options',
            status: 'pending'
          },
          {
            id: 'error-2',
            action: 'API returns 500 server error',
            expected: 'Extension displays user-friendly error message',
            status: 'pending'
          },
          {
            id: 'error-3',
            action: 'Network timeout occurs during task creation',
            expected: 'Extension offers to retry the operation',
            status: 'pending'
          },
          {
            id: 'error-4',
            action: 'Invalid data is received from API',
            expected: 'Extension handles gracefully without crashing',
            status: 'pending'
          },
          {
            id: 'error-5',
            action: 'Extension configuration is corrupted',
            expected: 'Extension resets to default config with user notification',
            status: 'pending'
          },
          {
            id: 'error-6',
            action: 'User attempts invalid operations',
            expected: 'Extension provides helpful validation messages',
            status: 'pending'
          }
        ]
      }
    ];

    setScenarios(defaultScenarios);
  };

  const runScenarioStep = async (scenarioId: string, stepId: string): Promise<{ success: boolean; duration: number; details?: string; error?: string }> => {
    const startTime = Date.now();
    
    // Simulate step execution with realistic delays
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    // Simulate realistic success/failure rates based on step type
    const success = Math.random() > 0.1; // 90% success rate
    
    return {
      success,
      duration: Date.now() - startTime,
      details: success ? `Step completed successfully` : undefined,
      error: success ? undefined : `Simulated failure for testing purposes`
    };
  };

  const runScenario = async (scenarioId: string) => {
    setIsRunning(true);
    const startTime = Date.now();

    // Update scenario status to running
    setScenarios(prev => prev.map(s => 
      s.id === scenarioId 
        ? { ...s, status: 'running' as const, steps: s.steps.map(step => ({ ...step, status: 'pending' as const })) }
        : s
    ));

    const scenario = scenarios.find(s => s.id === scenarioId);
    if (!scenario) return;

    let hasFailures = false;

    // Run each step sequentially
    for (const step of scenario.steps) {
      // Update step to running
      setScenarios(prev => prev.map(s => 
        s.id === scenarioId 
          ? { ...s, steps: s.steps.map(st => st.id === step.id ? { ...st, status: 'running' as const } : st) }
          : s
      ));

      const result = await runScenarioStep(scenarioId, step.id);

      // Update step with result
      setScenarios(prev => prev.map(s => 
        s.id === scenarioId 
          ? { 
              ...s, 
              steps: s.steps.map(st => 
                st.id === step.id 
                  ? { 
                      ...st, 
                      status: result.success ? 'passed' as const : 'failed' as const,
                      details: result.details || result.error
                    } 
                  : st
              ) 
            }
          : s
      ));

      if (!result.success) {
        hasFailures = true;
        toast.error(`Step failed: ${step.action}`);
        break; // Stop on first failure for scenarios
      } else {
        toast.success(`Step passed: ${step.action}`);
      }
    }

    // Update scenario final status
    const duration = Date.now() - startTime;
    setScenarios(prev => prev.map(s => 
      s.id === scenarioId 
        ? { 
            ...s, 
            status: hasFailures ? 'failed' as const : 'passed' as const,
            duration,
            error: hasFailures ? 'Scenario failed on one or more steps' : undefined
          }
        : s
    ));

    setIsRunning(false);
    toast[hasFailures ? 'error' : 'success'](`Scenario ${hasFailures ? 'failed' : 'completed successfully'}`);
  };

  const runAllScenarios = async () => {
    for (const scenario of scenarios) {
      await runScenario(scenario.id);
      // Brief pause between scenarios
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-600" />;
      case 'running': return <Clock className="h-4 w-4 text-blue-600 animate-spin" />;
      default: return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'passed': return <Badge className="bg-green-100 text-green-800">Passed</Badge>;
      case 'failed': return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case 'running': return <Badge className="bg-blue-100 text-blue-800">Running</Badge>;
      default: return <Badge variant="outline">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Scenario-Based Testing</h2>
          <p className="text-muted-foreground">
            Test real-world user scenarios for the complete GitHub App → Extension Server → DTM Extension workflow
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={() => setShowCreateForm(true)} 
            variant="outline"
            className="gap-2"
          >
            <Plus className="h-4 w-4" />
            Create Scenario
          </Button>
          <Button 
            onClick={runAllScenarios} 
            disabled={isRunning}
            className="gap-2"
          >
            <Play className="h-4 w-4" />
            Run All Scenarios
          </Button>
        </div>
      </div>

      {/* Scenarios Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="text-lg font-semibold mb-4">Test Scenarios</h3>
          <div className="space-y-4">
            {scenarios.map((scenario) => (
              <Card 
                key={scenario.id} 
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedScenario?.id === scenario.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => setSelectedScenario(scenario)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <User className="h-4 w-4" />
                      {scenario.name}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(scenario.status)}
                      <Button 
                        size="sm" 
                        onClick={(e) => {
                          e.stopPropagation();
                          runScenario(scenario.id);
                        }}
                        disabled={isRunning}
                      >
                        <Play className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <CardDescription className="text-sm">
                    {scenario.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-xs text-muted-foreground">
                      <strong>User Story:</strong> {scenario.userStory}
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-muted-foreground">Steps:</span>
                      <div className="flex gap-1">
                        {scenario.steps.map((step) => (
                          <div 
                            key={step.id} 
                            className={`w-2 h-2 rounded-full ${
                              step.status === 'passed' ? 'bg-green-500' :
                              step.status === 'failed' ? 'bg-red-500' :
                              step.status === 'running' ? 'bg-blue-500' :
                              'bg-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-muted-foreground">{scenario.steps.length} total</span>
                    </div>
                    {scenario.duration && (
                      <div className="text-xs text-muted-foreground">
                        Duration: {(scenario.duration / 1000).toFixed(1)}s
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Scenario Details */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Scenario Details</h3>
          {selectedScenario ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(selectedScenario.status)}
                  {selectedScenario.name}
                </CardTitle>
                <CardDescription>
                  {selectedScenario.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium text-sm mb-2">User Story</h4>
                  <p className="text-sm text-muted-foreground italic">
                    "{selectedScenario.userStory}"
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-sm mb-2">Preconditions</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {selectedScenario.preconditions.map((condition, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                        {condition}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium text-sm mb-2">Test Steps</h4>
                  <div className="space-y-2">
                    {selectedScenario.steps.map((step, index) => (
                      <div key={step.id} className="border rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-muted-foreground">
                            Step {index + 1}
                          </span>
                          {getStatusIcon(step.status)}
                        </div>
                        <div className="text-sm mb-1">
                          <strong>Action:</strong> {step.action}
                        </div>
                        <div className="text-sm text-muted-foreground mb-1">
                          <strong>Expected:</strong> {step.expected}
                        </div>
                        {step.details && (
                          <div className="text-xs text-blue-600">
                            <strong>Result:</strong> {step.details}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm mb-2">Expected Outcome</h4>
                  <p className="text-sm text-muted-foreground">
                    {selectedScenario.expectedOutcome}
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-64 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Eye className="h-8 w-8 mx-auto mb-2" />
                <p>Select a scenario to view details</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}