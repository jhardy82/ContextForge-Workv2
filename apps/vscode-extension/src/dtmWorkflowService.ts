/**
 * DTM-TASKMAN Enhanced Sync Service
 *
 * Handles the complete DTM-TASKMAN synchronization workflow
 * Collects DTM task types and transforms them into TaskMan expandable objects
 */

import * as vscode from "vscode";
import { DatabaseService, Project, Sprint, Task } from "./databaseService";
import { E2ETestingService } from "./e2eTestingService";
import { TodoGroup, TodoItem } from "./models";

export interface DTMSyncOptions {
  includeCompleted?: boolean;
  dateFilter?: {
    start?: string;
    end?: string;
  };
  statusFilter?: string[];
  priorityFilter?: string[];
  projectFilter?: string[];
  performanceMode?: "fast" | "thorough";
}

export interface DTMSyncWorkflowResult {
  success: boolean;
  message: string;
  duration: number;
  stages: {
    collection: DTMCollectionResult;
    transformation: DTMTransformationResult;
    validation: DTMValidationResult;
    integration: DTMIntegrationResult;
  };
  metrics: {
    totalProjects: number;
    totalSprints: number;
    totalTasks: number;
    totalGroups: number;
    totalItems: number;
    errors: number;
    warnings: number;
  };
  errors: string[];
  warnings: string[];
}

export interface DTMCollectionResult {
  projects: Project[];
  sprints: Sprint[];
  tasks: Task[];
  collectionTime: number;
  apiCalls: number;
  errors: string[];
}

export interface DTMTransformationResult {
  groups: TodoGroup[];
  items: TodoItem[];
  transformationTime: number;
  hierarchyDepth: number;
  mappingErrors: string[];
}

export interface DTMValidationResult {
  orphanedItems: number;
  duplicateIds: string[];
  integrityIssues: string[];
  validationTime: number;
  warningsCount: number;
}

export interface DTMIntegrationResult {
  treeUpdateTime: number;
  notificationsSent: number;
  cacheUpdated: boolean;
  integrationErrors: string[];
}

export class DTMSyncWorkflowService {
  private databaseService: DatabaseService;
  private testingService?: E2ETestingService;
  private progressCallback?: (
    stage: string,
    progress: number,
    message: string
  ) => void;
  private isRunning: boolean = false;

  constructor(databaseService: DatabaseService) {
    this.databaseService = databaseService;
  }

  /**
   * Set testing service for validation
   */
  public setTestingService(testingService: E2ETestingService): void {
    this.testingService = testingService;
  }

  /**
   * Set progress callback for UI updates
   */
  public setProgressCallback(
    callback: (stage: string, progress: number, message: string) => void
  ): void {
    this.progressCallback = callback;
  }

  /**
   * Check if sync workflow is currently running
   */
  public isWorkflowRunning(): boolean {
    return this.isRunning;
  }

  /**
   * Execute complete DTM-TASKMAN synchronization workflow
   */
  public async executeFullSyncWorkflow(
    options: DTMSyncOptions = {}
  ): Promise<DTMSyncWorkflowResult> {
    if (this.isRunning) {
      throw new Error("Sync workflow is already running");
    }

    const startTime = Date.now();
    this.isRunning = true;

    const result: DTMSyncWorkflowResult = {
      success: false,
      message: "",
      duration: 0,
      stages: {
        collection: {
          projects: [],
          sprints: [],
          tasks: [],
          collectionTime: 0,
          apiCalls: 0,
          errors: [],
        },
        transformation: {
          groups: [],
          items: [],
          transformationTime: 0,
          hierarchyDepth: 0,
          mappingErrors: [],
        },
        validation: {
          orphanedItems: 0,
          duplicateIds: [],
          integrityIssues: [],
          validationTime: 0,
          warningsCount: 0,
        },
        integration: {
          treeUpdateTime: 0,
          notificationsSent: 0,
          cacheUpdated: false,
          integrationErrors: [],
        },
      },
      metrics: {
        totalProjects: 0,
        totalSprints: 0,
        totalTasks: 0,
        totalGroups: 0,
        totalItems: 0,
        errors: 0,
        warnings: 0,
      },
      errors: [],
      warnings: [],
    };

    try {
      this.updateProgress(
        "initialization",
        0,
        "Initializing DTM sync workflow..."
      );

      // Stage 1: Data Collection from DTM
      this.updateProgress("collection", 10, "Starting DTM data collection...");
      result.stages.collection = await this.executeCollectionStage(options);

      if (result.stages.collection.errors.length > 0) {
        result.errors.push(...result.stages.collection.errors);
      }

      // Stage 2: Data Transformation to TaskMan Objects
      this.updateProgress(
        "transformation",
        40,
        "Transforming DTM data to TaskMan objects..."
      );
      result.stages.transformation = await this.executeTransformationStage(
        result.stages.collection.projects,
        result.stages.collection.sprints,
        result.stages.collection.tasks,
        options
      );

      if (result.stages.transformation.mappingErrors.length > 0) {
        result.errors.push(...result.stages.transformation.mappingErrors);
      }

      // Stage 3: Data Validation and Integrity Checks
      this.updateProgress("validation", 70, "Validating synchronized data...");
      result.stages.validation = await this.executeValidationStage(
        result.stages.transformation.groups,
        result.stages.transformation.items
      );

      if (result.stages.validation.integrityIssues.length > 0) {
        result.errors.push(...result.stages.validation.integrityIssues);
      }

      // Stage 4: Integration with TaskMan Tree View
      this.updateProgress(
        "integration",
        90,
        "Integrating with TaskMan tree view..."
      );
      result.stages.integration = await this.executeIntegrationStage(
        result.stages.transformation.groups,
        result.stages.transformation.items
      );

      if (result.stages.integration.integrationErrors.length > 0) {
        result.errors.push(...result.stages.integration.integrationErrors);
      }

      // Calculate final metrics
      result.metrics = {
        totalProjects: result.stages.collection.projects.length,
        totalSprints: result.stages.collection.sprints.length,
        totalTasks: result.stages.collection.tasks.length,
        totalGroups: result.stages.transformation.groups.length,
        totalItems: result.stages.transformation.items.length,
        errors: result.errors.length,
        warnings: result.warnings.length,
      };

      result.success = result.errors.length === 0;
      result.message = result.success
        ? `Successfully synchronized ${result.metrics.totalTasks} tasks across ${result.metrics.totalProjects} projects`
        : `Sync completed with ${result.errors.length} errors`;

      this.updateProgress("complete", 100, result.message);
    } catch (error: any) {
      result.success = false;
      result.message = `Sync workflow failed: ${error?.message || error}`;
      result.errors.push(error?.message || String(error));
    } finally {
      result.duration = Date.now() - startTime;
      this.isRunning = false;
    }

    return result;
  }

  /**
   * Execute DTM data collection stage
   */
  private async executeCollectionStage(
    options: DTMSyncOptions
  ): Promise<DTMCollectionResult> {
    const startTime = Date.now();
    const result: DTMCollectionResult = {
      projects: [],
      sprints: [],
      tasks: [],
      collectionTime: 0,
      apiCalls: 0,
      errors: [],
    };

    try {
      // Step 1: Collect Projects
      this.updateProgress("collection", 15, "Collecting projects from DTM...");
      result.projects = await this.collectDTMProjects(options);
      result.apiCalls++;

      // Step 2: Collect Sprints
      this.updateProgress("collection", 25, "Collecting sprints from DTM...");
      result.sprints = await this.collectDTMSprints(options, result.projects);
      result.apiCalls++;

      // Step 3: Collect Tasks (all task types from DTM)
      this.updateProgress(
        "collection",
        35,
        "Collecting all task types from DTM..."
      );
      result.tasks = await this.collectAllDTMTaskTypes(
        options,
        result.projects,
        result.sprints
      );
      result.apiCalls++;
    } catch (error: any) {
      result.errors.push(`Collection stage failed: ${error?.message || error}`);
    } finally {
      result.collectionTime = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Execute data transformation stage
   */
  private async executeTransformationStage(
    projects: Project[],
    sprints: Sprint[],
    tasks: Task[],
    options: DTMSyncOptions
  ): Promise<DTMTransformationResult> {
    const startTime = Date.now();
    const result: DTMTransformationResult = {
      groups: [],
      items: [],
      transformationTime: 0,
      hierarchyDepth: 0,
      mappingErrors: [],
    };

    try {
      // Transform DTM task types into TaskMan expandable objects
      this.updateProgress("transformation", 45, "Creating project groups...");
      const projectGroups = this.createProjectGroups(projects);
      result.groups.push(...projectGroups);

      this.updateProgress("transformation", 55, "Creating sprint groups...");
      const sprintGroups = this.createSprintGroups(sprints, projects);
      result.groups.push(...sprintGroups);

      this.updateProgress("transformation", 65, "Creating task items...");
      const taskItems = this.createTaskItems(tasks, result.groups);
      result.items.push(...taskItems);

      // Calculate hierarchy depth
      result.hierarchyDepth = this.calculateHierarchyDepth(result.groups);
    } catch (error: any) {
      result.mappingErrors.push(
        `Transformation failed: ${error?.message || error}`
      );
    } finally {
      result.transformationTime = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Execute validation stage
   */
  private async executeValidationStage(
    groups: TodoGroup[],
    items: TodoItem[]
  ): Promise<DTMValidationResult> {
    const startTime = Date.now();
    const result: DTMValidationResult = {
      orphanedItems: 0,
      duplicateIds: [],
      integrityIssues: [],
      validationTime: 0,
      warningsCount: 0,
    };

    try {
      // Check for orphaned items
      const groupIds = new Set(groups.map((g) => g.id));
      const orphanedItems = items.filter((item) => !groupIds.has(item.group));
      result.orphanedItems = orphanedItems.length;

      if (result.orphanedItems > 0) {
        result.integrityIssues.push(
          `Found ${result.orphanedItems} orphaned items`
        );
      }

      // Check for duplicate IDs
      const itemIds = items.map((item) => item.id);
      const duplicates = itemIds.filter(
        (id, index) => itemIds.indexOf(id) !== index
      );
      result.duplicateIds = [...new Set(duplicates)];

      if (result.duplicateIds.length > 0) {
        result.integrityIssues.push(
          `Found duplicate IDs: ${result.duplicateIds.join(", ")}`
        );
      }

      // Additional validation checks
      const emptyGroups = groups.filter(
        (group) => !items.some((item) => item.group === group.id)
      );

      if (emptyGroups.length > 0) {
        result.warningsCount++;
        // Empty groups are warnings, not errors
      }
    } catch (error: any) {
      result.integrityIssues.push(
        `Validation failed: ${error?.message || error}`
      );
    } finally {
      result.validationTime = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Execute integration stage
   */
  private async executeIntegrationStage(
    groups: TodoGroup[],
    items: TodoItem[]
  ): Promise<DTMIntegrationResult> {
    const startTime = Date.now();
    const result: DTMIntegrationResult = {
      treeUpdateTime: 0,
      notificationsSent: 0,
      cacheUpdated: false,
      integrationErrors: [],
    };

    try {
      // Update tree view with synchronized data
      this.updateProgress("integration", 95, "Updating TaskMan tree view...");
      await this.updateTaskManTreeView(groups, items);
      result.treeUpdateTime = Date.now() - startTime;

      // Send completion notifications
      result.notificationsSent = await this.sendSyncNotifications(
        groups.length,
        items.length
      );

      // Update cache
      result.cacheUpdated = await this.updateCache(groups, items);
    } catch (error: any) {
      result.integrationErrors.push(
        `Integration failed: ${error?.message || error}`
      );
    }

    return result;
  }

  /**
   * Collect all DTM projects
   */
  private async collectDTMProjects(
    options: DTMSyncOptions
  ): Promise<Project[]> {
    // In a real implementation, this would call the DTM API
    // For now, using the existing database service method
    try {
      const dtmData = await this.databaseService.loadFromDTMAPI();
      const projects = dtmData.projects;

      // Apply filters
      let filteredProjects = projects;

      if (options.statusFilter?.length) {
        filteredProjects = filteredProjects.filter(
          (p) => !p.status || options.statusFilter!.includes(p.status)
        );
      }

      if (options.projectFilter?.length) {
        filteredProjects = filteredProjects.filter((p) =>
          options.projectFilter!.includes(p.id)
        );
      }

      return filteredProjects;
    } catch (error) {
      console.error("Failed to collect DTM projects:", error);
      return [];
    }
  }

  /**
   * Collect all DTM sprints
   */
  private async collectDTMSprints(
    options: DTMSyncOptions,
    projects: Project[]
  ): Promise<Sprint[]> {
    // In a real implementation, this would call the DTM API
    try {
      const dtmData = await this.databaseService.loadFromDTMAPI();
      const sprints = dtmData.sprints;

      // Filter sprints to only include those for collected projects
      const projectIds = projects.map((p) => p.id);
      let filteredSprints = sprints.filter((s) =>
        projectIds.includes(s.project_id)
      );

      // Apply date filters
      if (options.dateFilter?.start || options.dateFilter?.end) {
        filteredSprints = filteredSprints.filter((s) => {
          if (
            options.dateFilter?.start &&
            s.start_date &&
            s.start_date < options.dateFilter.start
          ) {
            return false;
          }
          if (
            options.dateFilter?.end &&
            s.end_date &&
            s.end_date > options.dateFilter.end
          ) {
            return false;
          }
          return true;
        });
      }

      return filteredSprints;
    } catch (error) {
      console.error("Failed to collect DTM sprints:", error);
      return [];
    }
  }

  /**
   * Collect all DTM task types (the core of the DTM-TASKMAN sync)
   */
  private async collectAllDTMTaskTypes(
    options: DTMSyncOptions,
    projects: Project[],
    sprints: Sprint[]
  ): Promise<Task[]> {
    try {
      // Collect all open tasks, sprints, and projects from DTM
      // These are all considered "task types" in DTM terminology
      const dtmData = await this.databaseService.loadFromDTMAPI();
      const tasks = dtmData.tasks;

      // Filter tasks based on collected projects and sprints
      const projectIds = projects.map((p) => p.id);
      const sprintIds = sprints.map((s) => s.id);

      let filteredTasks = tasks.filter((t) => {
        // Include tasks that belong to collected projects or sprints
        const hasValidProject =
          !t.project_id || projectIds.includes(t.project_id);
        const hasValidSprint = !t.sprint_id || sprintIds.includes(t.sprint_id);
        return hasValidProject && hasValidSprint;
      });

      // Apply completion filter
      if (!options.includeCompleted) {
        filteredTasks = filteredTasks.filter(
          (t) =>
            !t.status ||
            !["completed", "done", "closed", "resolved"].includes(
              t.status.toLowerCase()
            )
        );
      }

      // Apply status filter
      if (options.statusFilter?.length) {
        filteredTasks = filteredTasks.filter(
          (t) => !t.status || options.statusFilter!.includes(t.status)
        );
      }

      // Apply priority filter
      if (options.priorityFilter?.length) {
        filteredTasks = filteredTasks.filter(
          (t) => !t.priority || options.priorityFilter!.includes(t.priority)
        );
      }

      return filteredTasks;
    } catch (error) {
      console.error("Failed to collect DTM task types:", error);
      return [];
    }
  }

  /**
   * Create project groups for TaskMan tree view
   */
  private createProjectGroups(projects: Project[]): TodoGroup[] {
    return projects.map((project) => {
      const group = new TodoGroup(`📋 ${project.name}`);
      group.description = project.mission || `Project: ${project.name}`;
      return group;
    });
  }

  /**
   * Create sprint groups for TaskMan tree view
   */
  private createSprintGroups(
    sprints: Sprint[],
    projects: Project[]
  ): TodoGroup[] {
    return sprints.map((sprint) => {
      const project = projects.find((p) => p.id === sprint.project_id);
      const group = new TodoGroup(`🏃 ${sprint.name}`);
      group.description = sprint.goal || `Sprint: ${sprint.name}`;
      if (project) {
        group.description += ` (${project.name})`;
      }
      return group;
    });
  }

  /**
   * Create task items for TaskMan tree view
   */
  private createTaskItems(tasks: Task[], groups: TodoGroup[]): TodoItem[] {
    return tasks.map((task) => {
      // Determine the appropriate group for this task
      let groupId = "ungrouped";

      if (task.sprint_id) {
        groupId = `sprint-${task.sprint_id}`;
      } else if (task.project_id) {
        groupId = `project-${task.project_id}`;
      }

      // Verify the group exists
      const groupExists = groups.some((g) => g.id === groupId);
      if (!groupExists) {
        groupId = "ungrouped";
      }

      const isCompleted = task.status
        ? ["completed", "done", "closed", "resolved"].includes(
            task.status.toLowerCase()
          )
        : false;

      const tags: string[] = [];
      if (task.priority) {
        tags.push(task.priority);
      }
      if (task.severity) {
        tags.push(task.severity);
      }
      if (task.owner) {
        tags.push(`@${task.owner}`);
      }

      return new TodoItem(
        task.id,
        task.title,
        isCompleted,
        groupId,
        task.description,
        task.due_date,
        tags
      );
    });
  }

  /**
   * Calculate hierarchy depth of groups
   */
  private calculateHierarchyDepth(groups: TodoGroup[]): number {
    // For now, we have a simple 2-level hierarchy (projects -> sprints)
    // This could be extended for deeper hierarchies
    return groups.length > 0 ? 2 : 0;
  }

  /**
   * Update TaskMan tree view with synchronized data
   */
  private async updateTaskManTreeView(
    groups: TodoGroup[],
    items: TodoItem[]
  ): Promise<void> {
    // This would integrate with the existing tree view provider
    // For now, just simulate the update
    await this.delay(100);

    // In a real implementation, this would:
    // 1. Clear existing tree data
    // 2. Add new groups and items
    // 3. Refresh the tree view
    // 4. Expand relevant nodes
  }

  /**
   * Send sync completion notifications
   */
  private async sendSyncNotifications(
    groupCount: number,
    itemCount: number
  ): Promise<number> {
    let notificationCount = 0;

    try {
      // Show information message about sync completion
      vscode.window.showInformationMessage(
        `DTM Sync Complete: ${itemCount} tasks organized into ${groupCount} groups`
      );
      notificationCount++;

      // Could also send other notifications (status bar, etc.)
    } catch (error) {
      console.error("Failed to send notifications:", error);
    }

    return notificationCount;
  }

  /**
   * Update cache with synchronized data
   */
  private async updateCache(
    groups: TodoGroup[],
    items: TodoItem[]
  ): Promise<boolean> {
    try {
      // In a real implementation, this would update a cache
      // For now, just simulate cache update
      await this.delay(50);
      return true;
    } catch (error) {
      console.error("Failed to update cache:", error);
      return false;
    }
  }

  /**
   * Update progress callback
   */
  private updateProgress(
    stage: string,
    progress: number,
    message: string
  ): void {
    if (this.progressCallback) {
      this.progressCallback(stage, progress, message);
    }
  }

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Get workflow status
   */
  public getWorkflowStatus(): {
    isRunning: boolean;
    currentStage?: string;
    progress?: number;
  } {
    return {
      isRunning: this.isRunning,
    };
  }
}
