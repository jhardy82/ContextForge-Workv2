import { Reporter, Task, TaskResult } from 'vitest'
import { writeFileSync, mkdirSync, existsSync } from 'fs'
import { join } from 'path'

interface TestMetrics {
  totalTests: number
  passed: number
  failed: number
  skipped: number
  duration: number
  coverage?: {
    lines: number
    functions: number
    branches: number
    statements: number
  }
}

interface TestReport {
  timestamp: string
  metrics: TestMetrics
  tests: Array<{
    name: string
    status: 'passed' | 'failed' | 'skipped'
    duration: number
    error?: string
    file: string
  }>
}

export class AdvancedTestReporter implements Reporter {
  private startTime = 0
  private report: TestReport = {
    timestamp: new Date().toISOString(),
    metrics: {
      totalTests: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      duration: 0
    },
    tests: []
  }

  onInit() {
    this.startTime = Date.now()
    console.log('🚀 Starting comprehensive test suite...')
  }

  onTestBegin(test: Task) {
    this.report.metrics.totalTests++
  }

  onTestFinished(test: Task, result: TaskResult) {
    const testInfo = {
      name: test.name,
      status: result.state as 'passed' | 'failed' | 'skipped',
      duration: result.duration || 0,
      file: test.file?.name || 'unknown',
      error: result.errors?.[0]?.message
    }

    this.report.tests.push(testInfo)

    switch (result.state) {
      case 'pass':
        this.report.metrics.passed++
        break
      case 'fail':
        this.report.metrics.failed++
        break
      default:
        this.report.metrics.skipped++
    }
  }

  onFinished() {
    this.report.metrics.duration = Date.now() - this.startTime
    this.generateReport()
    this.printSummary()
  }

  private generateReport() {
    const reportsDir = join(process.cwd(), 'test-results')
    
    if (!existsSync(reportsDir)) {
      mkdirSync(reportsDir, { recursive: true })
    }

    // Generate JSON report
    writeFileSync(
      join(reportsDir, 'test-report.json'),
      JSON.stringify(this.report, null, 2)
    )

    // Generate HTML report
    const htmlReport = this.generateHtmlReport()
    writeFileSync(
      join(reportsDir, 'test-report.html'),
      htmlReport
    )
  }

  private generateHtmlReport(): string {
    const { metrics, tests, timestamp } = this.report
    const successRate = ((metrics.passed / metrics.totalTests) * 100).toFixed(1)

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - ${timestamp}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { 
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value { font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem; }
        .metric-label { color: #64748b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .passed { color: #10b981; }
        .failed { color: #ef4444; }
        .skipped { color: #f59e0b; }
        .tests-table { 
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f1f5f9; padding: 1rem; text-align: left; font-weight: 600; }
        td { padding: 1rem; border-top: 1px solid #e2e8f0; }
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }
        .status-passed { background: #dcfce7; color: #166534; }
        .status-failed { background: #fecaca; color: #991b1b; }
        .status-skipped { background: #fef3c7; color: #a16207; }
        .duration { color: #64748b; font-size: 0.875rem; }
        .error { color: #ef4444; font-size: 0.875rem; max-width: 300px; word-break: break-word; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #059669);
            width: ${successRate}%;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Report</h1>
            <p>Generated on ${new Date(timestamp).toLocaleString()}</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p>Success Rate: ${successRate}%</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">${metrics.totalTests}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value passed">${metrics.passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value failed">${metrics.failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value skipped">${metrics.skipped}</div>
                <div class="metric-label">Skipped</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${(metrics.duration / 1000).toFixed(1)}s</div>
                <div class="metric-label">Duration</div>
            </div>
        </div>

        <div class="tests-table">
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>File</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
                    ${tests.map(test => `
                        <tr>
                            <td>${test.name}</td>
                            <td>${test.file}</td>
                            <td>
                                <span class="status-badge status-${test.status}">
                                    ${test.status}
                                </span>
                            </td>
                            <td class="duration">${test.duration}ms</td>
                            <td class="error">${test.error || ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
    `.trim()
  }

  private printSummary() {
    const { metrics } = this.report
    const successRate = ((metrics.passed / metrics.totalTests) * 100).toFixed(1)
    
    console.log('\n📊 Test Results Summary')
    console.log('========================')
    console.log(`✅ Passed: ${metrics.passed}`)
    console.log(`❌ Failed: ${metrics.failed}`)
    console.log(`⏭️  Skipped: ${metrics.skipped}`)
    console.log(`📈 Success Rate: ${successRate}%`)
    console.log(`⏱️  Duration: ${(metrics.duration / 1000).toFixed(1)}s`)
    
    if (metrics.failed > 0) {
      console.log('\n❌ Failed Tests:')
      this.report.tests
        .filter(test => test.status === 'failed')
        .forEach(test => {
          console.log(`   • ${test.name} (${test.file})`)
          if (test.error) {
            console.log(`     ${test.error}`)
          }
        })
    }

    console.log('\n📄 Reports generated in test-results/')
  }
}

export default AdvancedTestReporter