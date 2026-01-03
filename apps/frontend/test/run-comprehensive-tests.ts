#!/usr/bin/env node

/**
 * Comprehensive Test Suite Runner
 * Orchestrates execution of all test types: E2E, Accessibility, Performance, Visual, Smoke
 */

import { spawn } from "child_process";
import { promises as fs } from "fs";

interface TestSuite {
  name: string;
  command: string;
  args: string[];
  timeout: number;
  required: boolean;
  description: string;
}

interface TestResult {
  suite: string;
  success: boolean;
  duration: number;
  output: string;
  error?: string;
}

class ComprehensiveTestRunner {
  private results: TestResult[] = [];
  private startTime = Date.now();

  private testSuites: TestSuite[] = [
    {
      name: "smoke",
      command: "npx",
      args: ["playwright", "test", "--project=smoke", "--reporter=json"],
      timeout: 300000, // 5 minutes
      required: true,
      description: "Quick smoke tests to validate core functionality",
    },
    {
      name: "e2e-chromium",
      command: "npx",
      args: ["playwright", "test", "--project=e2e-chromium", "--reporter=json"],
      timeout: 900000, // 15 minutes
      required: true,
      description: "End-to-end tests in Chromium",
    },
    {
      name: "e2e-firefox",
      command: "npx",
      args: ["playwright", "test", "--project=e2e-firefox", "--reporter=json"],
      timeout: 900000, // 15 minutes
      required: false,
      description: "End-to-end tests in Firefox",
    },
    {
      name: "e2e-webkit",
      command: "npx",
      args: ["playwright", "test", "--project=e2e-webkit", "--reporter=json"],
      timeout: 900000, // 15 minutes
      required: false,
      description: "End-to-end tests in WebKit",
    },
    {
      name: "accessibility",
      command: "npx",
      args: [
        "playwright",
        "test",
        "--project=accessibility",
        "--reporter=json",
      ],
      timeout: 600000, // 10 minutes
      required: true,
      description: "WCAG compliance and accessibility testing",
    },
    {
      name: "performance",
      command: "npx",
      args: ["playwright", "test", "--project=performance", "--reporter=json"],
      timeout: 1200000, // 20 minutes
      required: true,
      description: "Core Web Vitals and performance testing",
    },
    {
      name: "visual-chromium",
      command: "npx",
      args: [
        "playwright",
        "test",
        "--project=visual-chromium",
        "--reporter=json",
      ],
      timeout: 900000, // 15 minutes
      required: true,
      description: "Visual regression testing in Chromium",
    },
    {
      name: "visual-firefox",
      command: "npx",
      args: [
        "playwright",
        "test",
        "--project=visual-firefox",
        "--reporter=json",
      ],
      timeout: 900000, // 15 minutes
      required: false,
      description: "Visual regression testing in Firefox",
    },
    {
      name: "visual-mobile",
      command: "npx",
      args: [
        "playwright",
        "test",
        "--project=visual-mobile",
        "--reporter=json",
      ],
      timeout: 900000, // 15 minutes
      required: true,
      description: "Visual regression testing on mobile",
    },
  ];

  async run(): Promise<void> {
    console.log("🚀 Starting Comprehensive Test Suite Execution");
    console.log("=".repeat(60));

    await this.ensureDirectories();
    await this.runTestSuites();
    await this.generateReport();

    const totalDuration = Date.now() - this.startTime;
    console.log(
      `\n✅ Test execution completed in ${Math.round(totalDuration / 1000)}s`
    );

    this.exitWithStatus();
  }

  private async ensureDirectories(): Promise<void> {
    const dirs = [
      "test-results",
      "test-results/playwright-report",
      "test-results/comprehensive-report",
      "test-results/screenshots",
      "test-results/videos",
      "test-results/traces",
    ];

    for (const dir of dirs) {
      try {
        await fs.mkdir(dir, { recursive: true });
      } catch (error) {
        // Directory might already exist
      }
    }
  }

  private async runTestSuites(): Promise<void> {
    // Run smoke tests first (fail fast)
    console.log("\n📋 Phase 1: Smoke Tests");
    console.log("-".repeat(30));

    const smokeResult = await this.runSuite(this.testSuites[0]);
    this.results.push(smokeResult);

    if (!smokeResult.success && smokeResult.suite === "smoke") {
      console.log("❌ Smoke tests failed. Aborting comprehensive test run.");
      return;
    }

    // Run core tests (E2E, Accessibility, Performance)
    console.log("\n🔧 Phase 2: Core Test Suites");
    console.log("-".repeat(30));

    const coreTests = this.testSuites.slice(1, 5); // e2e-chromium, accessibility, performance
    const corePromises = coreTests.map((suite) => this.runSuite(suite));
    const coreResults = await Promise.allSettled(corePromises);

    coreResults.forEach((result, index) => {
      if (result.status === "fulfilled") {
        this.results.push(result.value);
      } else {
        this.results.push({
          suite: coreTests[index].name,
          success: false,
          duration: 0,
          output: "",
          error: result.reason?.toString() || "Unknown error",
        });
      }
    });

    // Run visual and cross-browser tests (non-blocking)
    console.log("\n🎨 Phase 3: Visual & Cross-Browser Tests");
    console.log("-".repeat(30));

    const visualTests = this.testSuites.slice(5); // remaining visual and browser tests
    const visualPromises = visualTests.map((suite) => this.runSuite(suite));
    const visualResults = await Promise.allSettled(visualPromises);

    visualResults.forEach((result, index) => {
      if (result.status === "fulfilled") {
        this.results.push(result.value);
      } else {
        this.results.push({
          suite: visualTests[index].name,
          success: false,
          duration: 0,
          output: "",
          error: result.reason?.toString() || "Unknown error",
        });
      }
    });
  }

  private async runSuite(suite: TestSuite): Promise<TestResult> {
    console.log(`\n▶️  Running ${suite.name}: ${suite.description}`);

    const startTime = Date.now();
    let output = "";
    let error = "";

    return new Promise((resolve) => {
      const process = spawn(suite.command, suite.args, {
        stdio: ["pipe", "pipe", "pipe"],
        shell: true,
      });

      const timeout = setTimeout(() => {
        process.kill("SIGKILL");
        resolve({
          suite: suite.name,
          success: false,
          duration: Date.now() - startTime,
          output,
          error: `Test suite timed out after ${suite.timeout / 1000}s`,
        });
      }, suite.timeout);

      process.stdout?.on("data", (data) => {
        const chunk = data.toString();
        output += chunk;

        // Show progress for long-running suites
        if (
          chunk.includes("Running") ||
          chunk.includes("PASS") ||
          chunk.includes("FAIL")
        ) {
          process.stdout?.write(".");
        }
      });

      process.stderr?.on("data", (data) => {
        error += data.toString();
      });

      process.on("close", (code) => {
        clearTimeout(timeout);
        const duration = Date.now() - startTime;
        const success = code === 0;

        console.log(
          success ? " ✅" : " ❌",
          `(${Math.round(duration / 1000)}s)`
        );

        resolve({
          suite: suite.name,
          success,
          duration,
          output,
          error: success ? undefined : error,
        });
      });

      process.on("error", (err) => {
        clearTimeout(timeout);
        resolve({
          suite: suite.name,
          success: false,
          duration: Date.now() - startTime,
          output,
          error: err.message,
        });
      });
    });
  }

  private async generateReport(): Promise<void> {
    const totalDuration = Date.now() - this.startTime;
    const successCount = this.results.filter((r) => r.success).length;
    const failCount = this.results.filter((r) => !r.success).length;
    const requiredFailures = this.results.filter(
      (r) =>
        !r.success && this.testSuites.find((s) => s.name === r.suite)?.required
    ).length;

    const report = {
      summary: {
        total: this.results.length,
        passed: successCount,
        failed: failCount,
        requiredFailures,
        duration: totalDuration,
        timestamp: new Date().toISOString(),
      },
      results: this.results.map((r) => ({
        suite: r.suite,
        success: r.success,
        duration: r.duration,
        required:
          this.testSuites.find((s) => s.name === r.suite)?.required || false,
        description:
          this.testSuites.find((s) => s.name === r.suite)?.description || "",
        error: r.error,
      })),
    };

    // Generate JSON report
    await fs.writeFile(
      "test-results/comprehensive-report/summary.json",
      JSON.stringify(report, null, 2)
    );

    // Generate HTML report
    const htmlReport = this.generateHtmlReport(report);
    await fs.writeFile(
      "test-results/comprehensive-report/index.html",
      htmlReport
    );

    // Generate console summary
    console.log("\n" + "=".repeat(60));
    console.log("📊 COMPREHENSIVE TEST RESULTS SUMMARY");
    console.log("=".repeat(60));
    console.log(`Total Suites: ${report.summary.total}`);
    console.log(`✅ Passed: ${report.summary.passed}`);
    console.log(`❌ Failed: ${report.summary.failed}`);
    console.log(`⚠️  Required Failures: ${report.summary.requiredFailures}`);
    console.log(
      `⏱️  Total Duration: ${Math.round(report.summary.duration / 1000)}s`
    );

    console.log("\n📋 DETAILED RESULTS:");
    console.log("-".repeat(60));

    for (const result of report.results) {
      const status = result.success ? "✅" : "❌";
      const required = result.required ? "🔴" : "🟡";
      const duration = `${Math.round(result.duration / 1000)}s`;

      console.log(
        `${status} ${required} ${result.suite.padEnd(20)} ${duration.padStart(
          6
        )} - ${result.description}`
      );

      if (!result.success && result.error) {
        console.log(`    Error: ${result.error.substring(0, 100)}...`);
      }
    }

    console.log("\n📄 Reports generated:");
    console.log("   • test-results/comprehensive-report/index.html");
    console.log("   • test-results/comprehensive-report/summary.json");
    console.log(
      "   • test-results/playwright-report/ (Playwright HTML reports)"
    );
  }

  private generateHtmlReport(report: any): string {
    const statusIcon = (success: boolean) => (success ? "✅" : "❌");
    const requiredIcon = (required: boolean) => (required ? "🔴" : "🟡");

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTM Task Manager - Comprehensive Test Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 2rem;
            background: #f8fafc;
            color: #334155;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .metric {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            color: #64748b;
            font-size: 0.875rem;
        }
        .passed { color: #10b981; }
        .failed { color: #ef4444; }
        .warning { color: #f59e0b; }
        .results {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .results-header {
            background: #f1f5f9;
            padding: 1rem 1.5rem;
            font-weight: 600;
            border-bottom: 1px solid #e2e8f0;
        }
        .result-row {
            display: grid;
            grid-template-columns: 3rem 3rem 1fr 80px;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #f1f5f9;
        }
        .result-row:last-child {
            border-bottom: none;
        }
        .result-row:hover {
            background: #f8fafc;
        }
        .description {
            color: #64748b;
            font-size: 0.875rem;
        }
        .duration {
            text-align: right;
            font-weight: 500;
        }
        .error {
            grid-column: 1 / -1;
            margin-top: 0.5rem;
            padding: 0.75rem;
            background: #fef2f2;
            border: 1px solid #fed7d7;
            border-radius: 4px;
            color: #dc2626;
            font-size: 0.875rem;
            font-family: monospace;
        }
        .footer {
            margin-top: 2rem;
            text-align: center;
            color: #64748b;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>DTM Task Manager</h1>
        <p>Comprehensive Test Results - ${new Date(
          report.summary.timestamp
        ).toLocaleString()}</p>
    </div>

    <div class="summary">
        <div class="metric">
            <div class="metric-value">${report.summary.total}</div>
            <div class="metric-label">Total Suites</div>
        </div>
        <div class="metric">
            <div class="metric-value passed">${report.summary.passed}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value failed">${report.summary.failed}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value warning">${
              report.summary.requiredFailures
            }</div>
            <div class="metric-label">Critical Failures</div>
        </div>
        <div class="metric">
            <div class="metric-value">${Math.round(
              report.summary.duration / 1000
            )}s</div>
            <div class="metric-label">Total Duration</div>
        </div>
    </div>

    <div class="results">
        <div class="results-header">Test Suite Results</div>
        ${report.results
          .map(
            (result: any) => `
            <div class="result-row">
                <div>${statusIcon(result.success)}</div>
                <div>${requiredIcon(result.required)}</div>
                <div>
                    <div><strong>${result.suite}</strong></div>
                    <div class="description">${result.description}</div>
                    ${
                      result.error
                        ? `<div class="error">Error: ${result.error}</div>`
                        : ""
                    }
                </div>
                <div class="duration">${Math.round(
                  result.duration / 1000
                )}s</div>
            </div>
        `
          )
          .join("")}
    </div>

    <div class="footer">
        <p>🔴 Required • 🟡 Optional</p>
        <p>Generated by DTM Task Manager Test Suite</p>
    </div>
</body>
</html>`;
  }

  private exitWithStatus(): void {
    const requiredFailures = this.results.filter(
      (r) =>
        !r.success && this.testSuites.find((s) => s.name === r.suite)?.required
    ).length;

    if (requiredFailures > 0) {
      console.log(
        `\n❌ ${requiredFailures} required test suite(s) failed. Exiting with code 1.`
      );
      process.exit(1);
    } else {
      console.log("\n✅ All required test suites passed successfully!");
      process.exit(0);
    }
  }
}

// Run the comprehensive test suite
if (import.meta.url === `file://${process.argv[1]}`) {
  const runner = new ComprehensiveTestRunner();
  runner.run().catch((error) => {
    console.error("Failed to run comprehensive test suite:", error);
    process.exit(1);
  });
}

export default ComprehensiveTestRunner;
