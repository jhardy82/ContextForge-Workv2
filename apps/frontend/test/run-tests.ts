#!/usr/bin/env node

import { spawn } from 'child_process';

interface TestSuiteResult {
  name: string;
  type: 'unit' | 'integration' | 'e2e' | 'visual' | 'accessibility' | 'performance' | 'smoke';
  success: boolean;
  duration: number;
  output: string;
  error?: string;
}

class TestRunner {
  private results: TestSuiteResult[] = [];

  async runCommand(command: string, args: string[] = []): Promise<TestSuiteResult> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      const child = spawn(command, args, { 
        stdio: 'pipe',
        shell: true 
      });

      let output = '';
      let error = '';

      child.stdout?.on('data', (data) => {
        output += data.toString();
        if (process.env.VERBOSE_TESTS) {
          process.stdout.write(data);
        }
      });

      child.stderr?.on('data', (data) => {
        error += data.toString();
        if (process.env.VERBOSE_TESTS) {
          process.stderr.write(data);
        }
      });

      child.on('close', (code) => {
        const duration = Date.now() - startTime;
        resolve({
          name: `${command} ${args.join(' ')}`,
          type: this.inferTestType(command, args),
          success: code === 0,
          duration,
          output,
          error: code !== 0 ? error : undefined,
        });
      });
    });
  }

  private inferTestType(command: string, args: string[]): TestSuiteResult['type'] {
    const argString = args.join(' ');
    
    if (argString.includes('smoke')) return 'smoke';
    if (argString.includes('integration')) return 'integration';
    if (argString.includes('e2e') || command.includes('playwright')) {
      if (argString.includes('visual')) return 'visual';
      if (argString.includes('accessibility') || argString.includes('a11y')) return 'accessibility';
      if (argString.includes('performance')) return 'performance';
      return 'e2e';
    }
    return 'unit';
  }

  async runE2ETests(): Promise<TestSuiteResult> {
    console.log('🎭 Running E2E tests...');
    return this.runCommand('npx', ['playwright', 'test', '--reporter=html']);
  }

  async runE2ETestsHeadless(): Promise<TestSuiteResult> {
    console.log('🎭 Running E2E tests (headless)...');
    return this.runCommand('npx', ['playwright', 'test', '--headed=false']);
  }

  async runE2ETestsChrome(): Promise<TestSuiteResult> {
    console.log('🎭 Running E2E tests (Chrome only)...');
    return this.runCommand('npx', ['playwright', 'test', '--project=chromium']);
  }

  async runE2ETestsMobile(): Promise<TestSuiteResult> {
    console.log('📱 Running E2E tests (Mobile)...');
    return this.runCommand('npx', ['playwright', 'test', '--project=mobile-chrome', '--project=mobile-safari']);
  }

  async runSmokeTests(): Promise<TestSuiteResult> {
    console.log('💨 Running smoke tests...');
    return this.runCommand('npx', ['playwright', 'test', '--grep=@smoke']);
  }

  async runIntegrationTests(): Promise<TestSuiteResult> {
    console.log('🔗 Running integration tests...');
    return this.runCommand('npx', ['playwright', 'test', 'src/test/integration']);
  }

  async runVisualTests(): Promise<TestSuiteResult> {
    console.log('👁️ Running visual regression tests...');
    // Update screenshots first, then run comparison
    await this.runCommand('npx', ['playwright', 'test', '--update-snapshots']);
    return this.runCommand('npx', ['playwright', 'test', 'src/test/visual']);
  }

  async runAccessibilityTests(): Promise<TestSuiteResult> {
    console.log('♿ Running accessibility tests...');
    return this.runCommand('npx', ['playwright', 'test', 'src/test/accessibility']);
  }

  async runPerformanceTests(): Promise<TestSuiteResult> {
    console.log('⚡ Running performance tests...');
    return this.runCommand('npx', ['playwright', 'test', 'src/test/performance']);
  }

  async runAllTests(options: { 
    parallel?: boolean; 
    skipE2E?: boolean; 
    skipVisual?: boolean;
    fast?: boolean;
    headless?: boolean;
    project?: string;
  } = {}): Promise<TestSuiteResult[]> {
    console.log('🚀 Starting comprehensive test suite...\n');

    const testSuites: Promise<TestSuiteResult>[] = [];

    if (options.fast) {
      // Fast mode - only essential tests
      console.log('⚡ Fast mode - running essential tests only');
      testSuites.push(this.runSmokeTests());
      
      if (options.project) {
        testSuites.push(this.runCommand('npx', ['playwright', 'test', `--project=${options.project}`]));
      } else {
        testSuites.push(this.runE2ETestsChrome());
      }
    } else {
      // Full test suite
      testSuites.push(this.runSmokeTests());
      testSuites.push(this.runIntegrationTests());
      
      if (!options.skipE2E) {
        if (options.headless) {
          testSuites.push(this.runE2ETestsHeadless());
        } else {
          testSuites.push(this.runE2ETests());
        }
        testSuites.push(this.runE2ETestsMobile());
      }
      
      if (!options.skipVisual) {
        testSuites.push(this.runVisualTests());
      }
      
      testSuites.push(this.runAccessibilityTests());
      testSuites.push(this.runPerformanceTests());
    }

    if (options.parallel) {
      console.log('Running tests in parallel...');
      this.results = await Promise.allSettled(testSuites).then(results => 
        results.map((result, index) => 
          result.status === 'fulfilled' ? result.value : {
            name: `Test Suite ${index + 1}`,
            type: 'e2e' as const,
            success: false,
            duration: 0,
            output: '',
            error: result.reason?.toString() || 'Unknown error'
          }
        )
      );
    } else {
      console.log('Running tests sequentially...');
      this.results = [];
      for (const testSuite of testSuites) {
        try {
          const result = await testSuite;
          this.results.push(result);
          
          // Stop on first failure in sequential mode (optional)
          if (!result.success && process.env.FAIL_FAST === 'true') {
            console.log(`❌ Test suite failed: ${result.name}`);
            break;
          }
        } catch (error) {
          this.results.push({
            name: 'Failed Test Suite',
            type: 'e2e',
            success: false,
            duration: 0,
            output: '',
            error: error instanceof Error ? error.message : 'Unknown error'
          });
        }
      }
    }

    return this.results;
  }

  generateReport(): void {
    console.log('\n📊 Test reports generated by Playwright');
    console.log('   - HTML report: test-results/playwright-report/index.html');
    console.log('   - JSON report: test-results/playwright-results.json');
    console.log('   - JUnit report: test-results/playwright-junit.xml');
  }

  printSummary(): void {
    console.log('\n📈 Test Execution Summary');
    console.log('=' .repeat(50));

    const totalDuration = this.results.reduce((sum, r) => sum + r.duration, 0);
    const successfulTests = this.results.filter(r => r.success).length;
    const failedTests = this.results.filter(r => !r.success).length;

    console.log(`Total test suites: ${this.results.length}`);
    console.log(`Successful: ${successfulTests}`);
    console.log(`Failed: ${failedTests}`);
    console.log(`Total duration: ${(totalDuration / 1000).toFixed(2)}s`);
    console.log('');

    this.results.forEach(result => {
      const status = result.success ? '✅' : '❌';
      const duration = (result.duration / 1000).toFixed(2);
      console.log(`${status} ${result.type.padEnd(12)} ${duration}s - ${result.name}`);
      
      if (result.error) {
        console.log(`   Error: ${result.error.split('\n')[0]}`);
      }
    });

    console.log('');

    if (failedTests > 0) {
      console.log('❌ Some tests failed. Check the detailed output above.');
      console.log('💡 Run with --verbose for detailed test output');
      console.log('📄 Check the HTML report for detailed results');
      process.exit(1);
    } else {
      console.log('✅ All tests passed successfully!');
      console.log('📄 View the HTML report for detailed results');
    }
  }

  async showTestReport(): Promise<void> {
    console.log('🌐 Opening test report...');
    
    // Try to open the HTML report
    const openCommands = {
      darwin: 'open',
      win32: 'start',
      linux: 'xdg-open'
    };
    
    const command = openCommands[process.platform as keyof typeof openCommands];
    if (command) {
      try {
        await this.runCommand(command, ['test-results/playwright-report/index.html']);
      } catch (error) {
        console.log('Could not open report automatically. Please open test-results/playwright-report/index.html manually.');
      }
    }
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const options = {
    parallel: args.includes('--parallel'),
    skipE2E: args.includes('--skip-e2e'),
    skipVisual: args.includes('--skip-visual'),
    fast: args.includes('--fast'),
    headless: args.includes('--headless'),
    project: args.find(arg => arg.startsWith('--project='))?.split('=')[1],
  };

  // Set verbose mode
  if (args.includes('--verbose')) {
    process.env.VERBOSE_TESTS = 'true';
  }

  const runner = new TestRunner();

  try {
    await runner.runAllTests(options);
    runner.generateReport();
    runner.printSummary();
    
    if (args.includes('--open-report')) {
      await runner.showTestReport();
    }
  } catch (error) {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { TestRunner };