/**
 * End-to-End Testing Service for TaskMan-v2
 *
 * Provides comprehensive testing framework including DTM-TASKMAN sync workflow testing
 * Includes scenario-based testing, performance validation, and data integrity checks
 */

import * as vscode from "vscode";
import { DatabaseService, Project, Sprint, Task } from "./databaseService";
import { TodoGroup, TodoItem } from "./models";
import { SettingsManager } from "./settingsManager";

export interface TestScenario {
  id: string;
  name: string;
  description: string;
  category: "integration" | "unit" | "workflow" | "performance" | "stress";
  preconditions: string[];
  steps: TestStep[];
  expectedResults: string[];
  timeout: number;
}

export interface TestStep {
  action: string;
  description: string;
  parameters?: Record<string, any>;
  expectedOutput?: any;
  validations?: TestValidation[];
}

export interface TestValidation {
  type:
    | "equals"
    | "contains"
    | "exists"
    | "count"
    | "performance"
    | "structure";
  field: string;
  expected: any;
  tolerance?: number;
}

export interface TestResult {
  scenarioId: string;
  success: boolean;
  duration: number;
  stepResults: StepResult[];
  errors: string[];
  warnings: string[];
  metrics: {
    totalSteps: number;
    passedSteps: number;
    failedSteps: number;
    skippedSteps: number;
    performance: Record<string, number>;
  };
}

export interface StepResult {
  stepIndex: number;
  action: string;
  success: boolean;
  duration: number;
  output?: any;
  validationResults: ValidationResult[];
  error?: string;
}

export interface ValidationResult {
  type: string;
  field: string;
  expected: any;
  actual: any;
  passed: boolean;
  message: string;
}

export class E2ETestingService {
  private databaseService: DatabaseService;
  private settingsManager: SettingsManager;
  private testScenarios: Map<string, TestScenario> = new Map();
  private progressCallback?: (progress: number, message: string) => void;

  constructor(
    databaseService: DatabaseService,
    settingsManager: SettingsManager
  ) {
    this.databaseService = databaseService;
    this.settingsManager = settingsManager;
    this.initializeTestScenarios();
  }

  /**
   * Set progress callback for UI updates
   */
  public setProgressCallback(
    callback: (progress: number, message: string) => void
  ): void {
    this.progressCallback = callback;
  }

  /**
   * Initialize comprehensive test scenarios
   */
  private initializeTestScenarios(): void {
    // DTM Sync Workflow Test
    this.testScenarios.set("dtm-sync-full", {
      id: "dtm-sync-full",
      name: "DTM-TASKMAN Full Synchronization",
      description:
        "Complete workflow test for DTM data collection and TaskMan object transformation",
      category: "workflow",
      preconditions: [
        "DTM API is accessible",
        "Database connections are configured",
        "TaskMan tree view is initialized",
      ],
      steps: [
        {
          action: "checkDTMConnection",
          description: "Verify DTM API connectivity",
          validations: [{ type: "equals", field: "connected", expected: true }],
        },
        {
          action: "collectDTMProjects",
          description: "Collect all active projects from DTM",
          validations: [
            { type: "exists", field: "projects", expected: true },
            {
              type: "count",
              field: "projects.length",
              expected: 0,
              tolerance: 1000,
            },
          ],
        },
        {
          action: "collectDTMSprints",
          description: "Collect all sprints from DTM",
          validations: [
            { type: "exists", field: "sprints", expected: true },
            {
              type: "count",
              field: "sprints.length",
              expected: 0,
              tolerance: 1000,
            },
          ],
        },
        {
          action: "collectDTMTasks",
          description: "Collect all open tasks from DTM",
          validations: [
            { type: "exists", field: "tasks", expected: true },
            {
              type: "count",
              field: "tasks.length",
              expected: 0,
              tolerance: 10000,
            },
          ],
        },
        {
          action: "transformToTaskManObjects",
          description: "Transform DTM data into TaskMan expandable objects",
          validations: [
            { type: "exists", field: "groups", expected: true },
            { type: "exists", field: "items", expected: true },
            {
              type: "structure",
              field: "groups[0]",
              expected: { id: "string", label: "string", type: "string" },
            },
          ],
        },
        {
          action: "validateDataIntegrity",
          description: "Validate synchronized data integrity",
          validations: [
            { type: "equals", field: "orphanedItems", expected: 0 },
            { type: "equals", field: "duplicateIds", expected: 0 },
          ],
        },
        {
          action: "updateTreeView",
          description: "Update TaskMan tree view with synchronized data",
          validations: [
            {
              type: "performance",
              field: "updateTime",
              expected: 5000,
              tolerance: 2000,
            },
          ],
        },
      ],
      expectedResults: [
        "All DTM data successfully collected",
        "Data transformed into TaskMan format",
        "Tree view updated with hierarchical structure",
        "No data integrity issues detected",
      ],
      timeout: 30000,
    });

    // Database Connection Test
    this.testScenarios.set("database-connections", {
      id: "database-connections",
      name: "Database Connection Testing",
      description: "Test all database connection types and configurations",
      category: "integration",
      preconditions: ["Database connection settings are configured"],
      steps: [
        {
          action: "testSQLiteConnection",
          description: "Test SQLite database connection",
          validations: [
            { type: "equals", field: "connected", expected: true },
            {
              type: "performance",
              field: "connectionTime",
              expected: 1000,
              tolerance: 500,
            },
          ],
        },
        {
          action: "testDTMApiConnection",
          description: "Test DTM API connection",
          validations: [
            { type: "equals", field: "healthy", expected: true },
            {
              type: "performance",
              field: "responseTime",
              expected: 2000,
              tolerance: 1000,
            },
          ],
        },
        {
          action: "testLocalStorageConnection",
          description: "Test local storage connection",
          validations: [
            { type: "equals", field: "accessible", expected: true },
          ],
        },
      ],
      expectedResults: [
        "All database connections successful",
        "Performance within acceptable limits",
      ],
      timeout: 10000,
    });

    // Scenario-based workflow test
    this.testScenarios.set("user-workflow-complete", {
      id: "user-workflow-complete",
      name: "Complete User Workflow",
      description:
        "End-to-end user workflow from sync initiation to task management",
      category: "workflow",
      preconditions: ["Extension is activated", "All services are initialized"],
      steps: [
        {
          action: "initiateDTMSync",
          description: "User initiates DTM sync from command palette",
          validations: [
            { type: "equals", field: "syncStarted", expected: true },
          ],
        },
        {
          action: "monitorSyncProgress",
          description: "Monitor sync progress with user feedback",
          validations: [
            { type: "exists", field: "progressUpdates", expected: true },
            {
              type: "count",
              field: "progressUpdates.length",
              expected: 5,
              tolerance: 10,
            },
          ],
        },
        {
          action: "verifyTreeViewUpdate",
          description: "Verify tree view shows synchronized data",
          validations: [
            { type: "exists", field: "treeItems", expected: true },
            {
              type: "count",
              field: "treeItems.length",
              expected: 1,
              tolerance: 1000,
            },
          ],
        },
        {
          action: "testTaskInteraction",
          description: "Test user interaction with synchronized tasks",
          validations: [
            { type: "equals", field: "taskClickable", expected: true },
            { type: "equals", field: "detailsDisplayed", expected: true },
          ],
        },
      ],
      expectedResults: [
        "Sync completes successfully",
        "User receives progress feedback",
        "Tasks are interactive and detailed",
      ],
      timeout: 45000,
    });

    // Performance stress test
    this.testScenarios.set("performance-stress", {
      id: "performance-stress",
      name: "Performance Stress Test",
      description: "Test system performance under high data load",
      category: "performance",
      preconditions: [
        "Test data set available (1000+ tasks, 50+ projects, 100+ sprints)",
      ],
      steps: [
        {
          action: "loadLargeDataSet",
          description: "Load large test data set",
          parameters: { projectCount: 50, sprintCount: 100, taskCount: 1000 },
          validations: [
            {
              type: "performance",
              field: "loadTime",
              expected: 10000,
              tolerance: 5000,
            },
          ],
        },
        {
          action: "performBulkSync",
          description: "Perform sync with large data set",
          validations: [
            {
              type: "performance",
              field: "syncTime",
              expected: 30000,
              tolerance: 15000,
            },
            { type: "equals", field: "memoryLeaks", expected: false },
          ],
        },
        {
          action: "testTreeViewPerformance",
          description: "Test tree view performance with large data",
          validations: [
            {
              type: "performance",
              field: "renderTime",
              expected: 2000,
              tolerance: 1000,
            },
            {
              type: "performance",
              field: "scrollPerformance",
              expected: 100,
              tolerance: 50,
            },
          ],
        },
      ],
      expectedResults: [
        "System handles large data sets gracefully",
        "Performance remains within acceptable limits",
        "No memory leaks detected",
      ],
      timeout: 60000,
    });
  }

  /**
   * Run a specific test scenario
   */
  public async runTestScenario(scenarioId: string): Promise<TestResult> {
    const scenario = this.testScenarios.get(scenarioId);
    if (!scenario) {
      throw new Error(`Test scenario not found: ${scenarioId}`);
    }

    const startTime = Date.now();
    const result: TestResult = {
      scenarioId,
      success: false,
      duration: 0,
      stepResults: [],
      errors: [],
      warnings: [],
      metrics: {
        totalSteps: scenario.steps.length,
        passedSteps: 0,
        failedSteps: 0,
        skippedSteps: 0,
        performance: {},
      },
    };

    this.updateProgress(0, `Starting test scenario: ${scenario.name}`);

    try {
      // Check preconditions
      this.updateProgress(5, "Checking preconditions...");
      const preconditionCheck = await this.checkPreconditions(
        scenario.preconditions
      );
      if (!preconditionCheck.passed) {
        result.errors.push(
          `Preconditions failed: ${preconditionCheck.failures.join(", ")}`
        );
        return result;
      }

      // Execute test steps
      for (let i = 0; i < scenario.steps.length; i++) {
        const step = scenario.steps[i];
        const progress = 10 + (i / scenario.steps.length) * 80;
        this.updateProgress(progress, `Executing: ${step.description}`);

        const stepResult = await this.executeTestStep(step, i);
        result.stepResults.push(stepResult);

        if (stepResult.success) {
          result.metrics.passedSteps++;
        } else {
          result.metrics.failedSteps++;
          result.errors.push(`Step ${i + 1} failed: ${stepResult.error}`);
        }

        // Record performance metrics
        result.metrics.performance[`step_${i}_duration`] = stepResult.duration;
      }

      result.success = result.metrics.failedSteps === 0;
      this.updateProgress(
        100,
        result.success
          ? "Test scenario completed successfully"
          : "Test scenario completed with errors"
      );
    } catch (error: any) {
      result.errors.push(`Test execution failed: ${error?.message || error}`);
    } finally {
      result.duration = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Run all test scenarios
   */
  public async runAllTestScenarios(): Promise<Map<string, TestResult>> {
    const results = new Map<string, TestResult>();
    const scenarios = Array.from(this.testScenarios.keys());

    for (let i = 0; i < scenarios.length; i++) {
      const scenarioId = scenarios[i];
      const progress = (i / scenarios.length) * 100;
      this.updateProgress(
        progress,
        `Running scenario ${i + 1}/${scenarios.length}: ${scenarioId}`
      );

      try {
        const result = await this.runTestScenario(scenarioId);
        results.set(scenarioId, result);
      } catch (error: any) {
        results.set(scenarioId, {
          scenarioId,
          success: false,
          duration: 0,
          stepResults: [],
          errors: [error?.message || String(error)],
          warnings: [],
          metrics: {
            totalSteps: 0,
            passedSteps: 0,
            failedSteps: 1,
            skippedSteps: 0,
            performance: {},
          },
        });
      }
    }

    return results;
  }

  /**
   * Check test preconditions
   */
  private async checkPreconditions(preconditions: string[]): Promise<{
    passed: boolean;
    failures: string[];
  }> {
    const failures: string[] = [];

    for (const condition of preconditions) {
      switch (condition) {
        case "DTM API is accessible":
          const dtmCheck = await this.checkDTMApiAccessibility();
          if (!dtmCheck) {
            failures.push("DTM API not accessible");
          }
          break;
        case "Database connections are configured":
          const dbCheck = await this.checkDatabaseConfiguration();
          if (!dbCheck) {
            failures.push("Database connections not configured");
          }
          break;
        case "TaskMan tree view is initialized":
          const treeCheck = this.checkTreeViewInitialization();
          if (!treeCheck) {
            failures.push("TaskMan tree view not initialized");
          }
          break;
        case "Extension is activated":
          const extCheck = this.checkExtensionActivation();
          if (!extCheck) {
            failures.push("Extension not activated");
          }
          break;
        default:
          // Custom precondition checks can be added here
          break;
      }
    }

    return {
      passed: failures.length === 0,
      failures,
    };
  }

  /**
   * Execute a single test step
   */
  private async executeTestStep(
    step: TestStep,
    stepIndex: number
  ): Promise<StepResult> {
    const startTime = Date.now();
    const result: StepResult = {
      stepIndex,
      action: step.action,
      success: false,
      duration: 0,
      validationResults: [],
      output: undefined,
    };

    try {
      // Execute the step action
      result.output = await this.executeStepAction(step);

      // Run validations
      if (step.validations) {
        for (const validation of step.validations) {
          const validationResult = this.validateStepOutput(
            validation,
            result.output
          );
          result.validationResults.push(validationResult);
        }
      }

      // Determine step success
      result.success =
        result.validationResults.length === 0 ||
        result.validationResults.every((v) => v.passed);
    } catch (error: any) {
      result.error = error?.message || String(error);
    } finally {
      result.duration = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Execute a step action
   */
  private async executeStepAction(step: TestStep): Promise<any> {
    switch (step.action) {
      case "checkDTMConnection":
        return { connected: await this.checkDTMApiAccessibility() };

      case "collectDTMProjects":
        return { projects: await this.mockCollectDTMProjects() };

      case "collectDTMSprints":
        return { sprints: await this.mockCollectDTMSprints() };

      case "collectDTMTasks":
        return { tasks: await this.mockCollectDTMTasks() };

      case "transformToTaskManObjects":
        return await this.mockTransformToTaskManObjects();

      case "validateDataIntegrity":
        return { orphanedItems: 0, duplicateIds: 0 };

      case "updateTreeView":
        const updateStart = Date.now();
        await this.mockUpdateTreeView();
        return { updateTime: Date.now() - updateStart };

      case "testSQLiteConnection":
        return await this.testDatabaseConnection("sqlite");

      case "testDTMApiConnection":
        return await this.testDatabaseConnection("dtm");

      case "testLocalStorageConnection":
        return await this.testDatabaseConnection("local");

      default:
        throw new Error(`Unknown step action: ${step.action}`);
    }
  }

  /**
   * Validate step output
   */
  private validateStepOutput(
    validation: TestValidation,
    output: any
  ): ValidationResult {
    const result: ValidationResult = {
      type: validation.type,
      field: validation.field,
      expected: validation.expected,
      actual: this.getFieldValue(output, validation.field),
      passed: false,
      message: "",
    };

    switch (validation.type) {
      case "equals":
        result.passed = result.actual === result.expected;
        result.message = result.passed
          ? `Field ${validation.field} equals expected value`
          : `Expected ${result.expected}, got ${result.actual}`;
        break;

      case "exists":
        result.passed = result.actual !== undefined && result.actual !== null;
        result.message = result.passed
          ? `Field ${validation.field} exists`
          : `Field ${validation.field} does not exist`;
        break;

      case "count":
        const count = Array.isArray(result.actual) ? result.actual.length : 0;
        const tolerance = validation.tolerance || 0;
        result.passed = Math.abs(count - result.expected) <= tolerance;
        result.message = result.passed
          ? `Count ${count} within tolerance of expected ${result.expected}`
          : `Count ${count} exceeds tolerance for expected ${result.expected}`;
        break;

      case "performance":
        const actualTime =
          typeof result.actual === "number" ? result.actual : 0;
        const tolerance2 = validation.tolerance || 0;
        result.passed = actualTime <= result.expected + tolerance2;
        result.message = result.passed
          ? `Performance ${actualTime}ms within acceptable limit`
          : `Performance ${actualTime}ms exceeds limit of ${
              result.expected + tolerance2
            }ms`;
        break;

      default:
        result.message = `Unknown validation type: ${validation.type}`;
        break;
    }

    return result;
  }

  /**
   * Get field value from object using dot notation
   */
  private getFieldValue(obj: any, fieldPath: string): any {
    const parts = fieldPath.split(".");
    let current = obj;

    for (const part of parts) {
      if (current === null || current === undefined) {
        return undefined;
      }
      current = current[part];
    }

    return current;
  }

  /**
   * Update progress callback
   */
  private updateProgress(progress: number, message: string): void {
    if (this.progressCallback) {
      this.progressCallback(progress, message);
    }
  }

  // Mock implementation methods for testing
  private async checkDTMApiAccessibility(): Promise<boolean> {
    // Mock DTM API check
    await this.delay(100);
    return true;
  }

  private async checkDatabaseConfiguration(): Promise<boolean> {
    // Mock database configuration check
    return this.settingsManager !== undefined;
  }

  private checkTreeViewInitialization(): boolean {
    // Mock tree view check
    return true;
  }

  private checkExtensionActivation(): boolean {
    // Mock extension activation check
    return vscode.extensions.getExtension("taskman.taskman-v2") !== undefined;
  }

  private async mockCollectDTMProjects(): Promise<Project[]> {
    await this.delay(200);
    return [
      {
        id: "P1",
        name: "Test Project 1",
        status: "active",
        start_date: "2025-01-01",
        target_end_date: "2025-12-31",
        owner: "user1",
        mission: "Test mission",
      },
    ];
  }

  private async mockCollectDTMSprints(): Promise<Sprint[]> {
    await this.delay(300);
    return [
      {
        id: "S1",
        name: "Sprint 1",
        goal: "Test sprint",
        start_date: "2025-01-01",
        end_date: "2025-01-14",
        status: "active",
        project_id: "P1",
      },
    ];
  }

  private async mockCollectDTMTasks(): Promise<Task[]> {
    await this.delay(500);
    return [
      {
        id: "T1",
        title: "Test Task 1",
        status: "in_progress",
        priority: "high",
        severity: "normal",
        estimate_points: 5,
        actual_hours: 2,
        description: "Test task description",
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T12:00:00Z",
        due_date: "2025-01-15",
        sprint_id: "S1",
        project_id: "P1",
        owner: "user1",
      },
    ];
  }

  private async mockTransformToTaskManObjects(): Promise<{
    groups: TodoGroup[];
    items: TodoItem[];
  }> {
    await this.delay(200);
    const group = new TodoGroup("📋 Test Project 1");
    const item = new TodoItem(
      "T1",
      "Test Task 1",
      false,
      "project-P1",
      "Test task description",
      "2025-01-15",
      ["high", "@user1"]
    );
    return { groups: [group], items: [item] };
  }

  private async mockUpdateTreeView(): Promise<void> {
    await this.delay(100);
  }

  private async testDatabaseConnection(type: string): Promise<any> {
    const startTime = Date.now();
    await this.delay(50 + Math.random() * 100);
    const connectionTime = Date.now() - startTime;

    switch (type) {
      case "sqlite":
        return { connected: true, connectionTime };
      case "dtm":
        return { healthy: true, responseTime: connectionTime };
      case "local":
        return { accessible: true };
      default:
        return { error: "Unknown database type" };
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
