import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock, 
  ChartBar, 
  Eye, 
  Lightning, 
  Shield,
  GitBranch,
  Users
} from '@phosphor-icons/react'

interface TestMetrics {
  type: string
  icon: React.ReactNode
  total: number
  passed: number
  failed: number
  duration: string
  coverage?: number
  status: 'running' | 'passed' | 'failed' | 'pending'
}

export default function TestDashboard() {
  const [testMetrics, setTestMetrics] = useState<TestMetrics[]>([
    {
      type: 'Unit Tests',
      icon: <CheckCircle className="h-5 w-5" />,
      total: 47,
      passed: 45,
      failed: 2,
      duration: '12.3s',
      coverage: 87,
      status: 'passed'
    },
    {
      type: 'Integration Tests',
      icon: <GitBranch className="h-5 w-5" />,
      total: 23,
      passed: 21,
      failed: 2,
      duration: '8.7s',
      coverage: 82,
      status: 'failed'
    },
    {
      type: 'E2E Tests',
      icon: <Users className="h-5 w-5" />,
      total: 15,
      passed: 15,
      failed: 0,
      duration: '45.2s',
      status: 'passed'
    },
    {
      type: 'Visual Tests',
      icon: <Eye className="h-5 w-5" />,
      total: 12,
      passed: 11,
      failed: 1,
      duration: '23.1s',
      status: 'failed'
    },
    {
      type: 'Performance Tests',
      icon: <Lightning className="h-5 w-5" />,
      total: 8,
      passed: 8,
      failed: 0,
      duration: '31.4s',
      status: 'passed'
    },
    {
      type: 'Accessibility Tests',
      icon: <Shield className="h-5 w-5" />,
      total: 10,
      passed: 9,
      failed: 1,
      duration: '15.8s',
      status: 'failed'
    }
  ])

  const [isRunning, setIsRunning] = useState(false)
  const [selectedTest, setSelectedTest] = useState<TestMetrics | null>(null)

  const runAllTests = () => {
    setIsRunning(true)
    
    // Simulate test execution
    setTimeout(() => {
      setTestMetrics(prev => prev.map(test => ({
        ...test,
        status: Math.random() > 0.2 ? 'passed' : 'failed'
      })))
      setIsRunning(false)
    }, 3000)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      case 'running': return 'text-blue-600'
      default: return 'text-gray-500'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'passed': return <Badge className="bg-green-100 text-green-800">Passed</Badge>
      case 'failed': return <Badge className="bg-red-100 text-red-800">Failed</Badge>
      case 'running': return <Badge className="bg-blue-100 text-blue-800">Running</Badge>
      default: return <Badge variant="outline">Pending</Badge>
    }
  }

  const totalTests = testMetrics.reduce((sum, test) => sum + test.total, 0)
  const totalPassed = testMetrics.reduce((sum, test) => sum + test.passed, 0)
  const totalFailed = testMetrics.reduce((sum, test) => sum + test.failed, 0)
  const successRate = Math.round((totalPassed / totalTests) * 100)

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">🧪 Testing Dashboard</h1>
            <p className="text-muted-foreground">
              Comprehensive test monitoring and reporting
            </p>
          </div>
          <Button onClick={runAllTests} disabled={isRunning} className="gap-2">
            <Play className="h-4 w-4" />
            {isRunning ? 'Running Tests...' : 'Run All Tests'}
          </Button>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Tests</p>
                  <p className="text-2xl font-bold">{totalTests}</p>
                </div>
                <ChartBar className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Passed</p>
                  <p className="text-2xl font-bold text-green-600">{totalPassed}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Failed</p>
                  <p className="text-2xl font-bold text-red-600">{totalFailed}</p>
                </div>
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold">{successRate}%</p>
                </div>
                <div className="w-full mt-2">
                  <Progress value={successRate} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="results">Test Results</TabsTrigger>
            <TabsTrigger value="coverage">Coverage</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {testMetrics.map((test, index) => (
                <Card 
                  key={index} 
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setSelectedTest(test)}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <span className={getStatusColor(test.status)}>
                        {test.icon}
                      </span>
                      {test.type}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-2">
                      {getStatusBadge(test.status)}
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {test.duration}
                      </span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Passed</span>
                        <span className="text-sm font-medium text-green-600">{test.passed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Failed</span>
                        <span className="text-sm font-medium text-red-600">{test.failed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Total</span>
                        <span className="text-sm font-medium">{test.total}</span>
                      </div>
                      {test.coverage && (
                        <div className="mt-2">
                          <div className="flex justify-between mb-1">
                            <span className="text-xs text-muted-foreground">Coverage</span>
                            <span className="text-xs font-medium">{test.coverage}%</span>
                          </div>
                          <Progress value={test.coverage} className="h-1" />
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Test Results</CardTitle>
                <CardDescription>
                  Detailed breakdown of test execution results
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {testMetrics.map((test, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className={getStatusColor(test.status)}>
                          {test.icon}
                        </span>
                        <div>
                          <p className="font-medium">{test.type}</p>
                          <p className="text-sm text-muted-foreground">
                            {test.passed}/{test.total} tests passed
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {getStatusBadge(test.status)}
                        <span className="text-sm text-muted-foreground">{test.duration}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="coverage" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Code Coverage</CardTitle>
                  <CardDescription>Line and branch coverage metrics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { label: 'Lines', value: 87 },
                    { label: 'Functions', value: 92 },
                    { label: 'Branches', value: 78 },
                    { label: 'Statements', value: 85 }
                  ].map((item, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">{item.label}</span>
                        <span className="text-sm text-muted-foreground">{item.value}%</span>
                      </div>
                      <Progress value={item.value} className="h-2" />
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Coverage Trend</CardTitle>
                  <CardDescription>Coverage changes over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                    📈 Coverage trend chart would go here
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reports" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { title: 'HTML Coverage Report', description: 'Interactive coverage analysis', icon: '📊' },
                { title: 'Playwright Report', description: 'E2E test results and traces', icon: '🎭' },
                { title: 'Visual Diff Report', description: 'Screenshot comparisons', icon: '👁️' },
                { title: 'Performance Report', description: 'Core Web Vitals and metrics', icon: '⚡' },
                { title: 'Accessibility Report', description: 'WCAG compliance results', icon: '♿' },
                { title: 'Test Summary', description: 'Comprehensive test overview', icon: '📋' }
              ].map((report, index) => (
                <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{report.icon}</span>
                      <div>
                        <h3 className="font-medium">{report.title}</h3>
                        <p className="text-sm text-muted-foreground">{report.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Selected Test Details Modal would go here */}
        {selectedTest && (
          <Card className="fixed inset-4 z-50 max-w-2xl mx-auto bg-background border shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  {selectedTest.icon}
                  {selectedTest.type} Details
                </span>
                <Button variant="ghost" size="sm" onClick={() => setSelectedTest(null)}>
                  ✕
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">Status</p>
                    <p className="text-lg">{getStatusBadge(selectedTest.status)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Duration</p>
                    <p className="text-lg">{selectedTest.duration}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Success Rate</p>
                    <p className="text-lg">{Math.round((selectedTest.passed / selectedTest.total) * 100)}%</p>
                  </div>
                  {selectedTest.coverage && (
                    <div>
                      <p className="text-sm font-medium">Coverage</p>
                      <p className="text-lg">{selectedTest.coverage}%</p>
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">Test Breakdown</p>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span>✅ Passed</span>
                      <span>{selectedTest.passed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>❌ Failed</span>
                      <span>{selectedTest.failed}</span>
                    </div>
                    <div className="flex justify-between font-medium">
                      <span>📊 Total</span>
                      <span>{selectedTest.total}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}