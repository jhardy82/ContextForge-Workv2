import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

interface TestResult {
  name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
  coverage?: number;
}

interface TestSuite {
  name: string;
  type: 'unit' | 'integration' | 'e2e' | 'visual' | 'accessibility' | 'performance' | 'smoke';
  results: TestResult[];
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  duration: number;
  coverage?: number;
}

interface TestReport {
  timestamp: number;
  environment: string;
  totalSuites: number;
  totalTests: number;
  totalPassed: number;
  totalFailed: number;
  totalSkipped: number;
  totalDuration: number;
  overallCoverage: number;
  suites: TestSuite[];
}

export class TestReportGenerator {
  private reportDir: string;

  constructor(reportDir = './test-results/reports') {
    this.reportDir = reportDir;
    this.ensureReportDirectory();
  }

  private ensureReportDirectory() {
    if (!existsSync(this.reportDir)) {
      mkdirSync(this.reportDir, { recursive: true });
    }
  }

  generateReport(suites: TestSuite[]): TestReport {
    const totalTests = suites.reduce((sum, suite) => sum + suite.totalTests, 0);
    const totalPassed = suites.reduce((sum, suite) => sum + suite.passedTests, 0);
    const totalFailed = suites.reduce((sum, suite) => sum + suite.failedTests, 0);
    const totalSkipped = suites.reduce((sum, suite) => sum + suite.skippedTests, 0);
    const totalDuration = suites.reduce((sum, suite) => sum + suite.duration, 0);
    
    const suitesWithCoverage = suites.filter(suite => suite.coverage !== undefined);
    const overallCoverage = suitesWithCoverage.length > 0
      ? suitesWithCoverage.reduce((sum, suite) => sum + (suite.coverage || 0), 0) / suitesWithCoverage.length
      : 0;

    return {
      timestamp: Date.now(),
      environment: process.env.NODE_ENV || 'test',
      totalSuites: suites.length,
      totalTests,
      totalPassed,
      totalFailed,
      totalSkipped,
      totalDuration,
      overallCoverage,
      suites,
    };
  }

  generateHtmlReport(report: TestReport): string {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - ${new Date(report.timestamp).toLocaleString()}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .stat-label { color: #6c757d; font-size: 14px; }
        .passed { color: #28a745; }
        .failed { color: #dc3545; }
        .skipped { color: #ffc107; }
        .suite { background: white; border: 1px solid #e9ecef; border-radius: 8px; margin: 15px 0; padding: 20px; }
        .suite-header { display: flex; justify-content: between; align-items: center; margin-bottom: 15px; }
        .suite-title { font-size: 18px; font-weight: bold; }
        .suite-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .test-result { display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid #f8f9fa; }
        .test-name { flex: 1; }
        .test-status { padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
        .test-duration { color: #6c757d; font-size: 12px; margin-left: 10px; }
        .coverage-bar { background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .coverage-fill { background: #28a745; height: 100%; transition: width 0.3s ease; }
        .error-details { background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; padding: 10px; margin-top: 10px; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Test Report</h1>
        <p>Generated on ${new Date(report.timestamp).toLocaleString()}</p>
        <p>Environment: ${report.environment}</p>
    </div>

    <div class="summary">
        <div class="stat-card">
            <div class="stat-number">${report.totalSuites}</div>
            <div class="stat-label">Test Suites</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${report.totalTests}</div>
            <div class="stat-label">Total Tests</div>
        </div>
        <div class="stat-card">
            <div class="stat-number passed">${report.totalPassed}</div>
            <div class="stat-label">Passed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number failed">${report.totalFailed}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number skipped">${report.totalSkipped}</div>
            <div class="stat-label">Skipped</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${(report.totalDuration / 1000).toFixed(2)}s</div>
            <div class="stat-label">Duration</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${report.overallCoverage.toFixed(1)}%</div>
            <div class="stat-label">Coverage</div>
        </div>
    </div>

    ${report.suites.map(suite => `
        <div class="suite">
            <div class="suite-header">
                <div class="suite-title">${suite.name}</div>
                <div class="suite-badge" style="background: ${this.getSuiteColor(suite.type)}; color: white;">
                    ${suite.type.toUpperCase()}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 15px;">
                <div><strong>Tests:</strong> ${suite.totalTests}</div>
                <div><strong>Passed:</strong> <span class="passed">${suite.passedTests}</span></div>
                <div><strong>Failed:</strong> <span class="failed">${suite.failedTests}</span></div>
                <div><strong>Duration:</strong> ${(suite.duration / 1000).toFixed(2)}s</div>
            </div>

            ${suite.coverage !== undefined ? `
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Coverage</span>
                        <span>${suite.coverage.toFixed(1)}%</span>
                    </div>
                    <div class="coverage-bar">
                        <div class="coverage-fill" style="width: ${suite.coverage}%"></div>
                    </div>
                </div>
            ` : ''}

            <div>
                ${suite.results.map(result => `
                    <div class="test-result">
                        <div class="test-name">${result.name}</div>
                        <div>
                            <span class="test-status" style="background: ${this.getStatusColor(result.status)}; color: white;">
                                ${result.status}
                            </span>
                            <span class="test-duration">${result.duration}ms</span>
                        </div>
                    </div>
                    ${result.error ? `<div class="error-details">${result.error}</div>` : ''}
                `).join('')}
            </div>
        </div>
    `).join('')}

    <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center; color: #6c757d;">
        <p>Generated by VS Code Extension Testing Infrastructure</p>
        <p>Report includes Unit, Integration, E2E, Visual, Accessibility, and Performance tests</p>
    </div>
</body>
</html>
    `;

    return html;
  }

  private getSuiteColor(type: string): string {
    const colors = {
      unit: '#007bff',
      integration: '#28a745',
      e2e: '#17a2b8',
      visual: '#ffc107',
      accessibility: '#6f42c1',
      performance: '#fd7e14',
      smoke: '#20c997',
    };
    return colors[type as keyof typeof colors] || '#6c757d';
  }

  private getStatusColor(status: string): string {
    const colors = {
      passed: '#28a745',
      failed: '#dc3545',
      skipped: '#ffc107',
    };
    return colors[status as keyof typeof colors] || '#6c757d';
  }

  saveHtmlReport(report: TestReport, filename = 'test-report.html'): string {
    const html = this.generateHtmlReport(report);
    const filePath = join(this.reportDir, filename);
    writeFileSync(filePath, html, 'utf8');
    return filePath;
  }

  saveJsonReport(report: TestReport, filename = 'test-report.json'): string {
    const filePath = join(this.reportDir, filename);
    writeFileSync(filePath, JSON.stringify(report, null, 2), 'utf8');
    return filePath;
  }

  generateSummaryReport(reports: TestReport[]): any {
    const summary = {
      totalReports: reports.length,
      dateRange: {
        from: new Date(Math.min(...reports.map(r => r.timestamp))).toISOString(),
        to: new Date(Math.max(...reports.map(r => r.timestamp))).toISOString(),
      },
      trends: {
        passRate: reports.map(r => (r.totalPassed / r.totalTests) * 100),
        coverage: reports.map(r => r.overallCoverage),
        duration: reports.map(r => r.totalDuration),
      },
      averages: {
        passRate: reports.reduce((sum, r) => sum + (r.totalPassed / r.totalTests), 0) / reports.length * 100,
        coverage: reports.reduce((sum, r) => sum + r.overallCoverage, 0) / reports.length,
        duration: reports.reduce((sum, r) => sum + r.totalDuration, 0) / reports.length,
      },
    };

    return summary;
  }
}

export default TestReportGenerator;