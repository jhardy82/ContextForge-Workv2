import { Project, Sprint, Task, TaskStatus } from "@/types/objects";
import { toast } from "sonner";

const STORAGE_KEY = "taskman_mock_db";
const DELAY_MS = 300;

interface MockDb {
  projects: Project[];
  sprints: Sprint[];
  tasks: Task[];
}

const getDb = (): MockDb => {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { projects: [], sprints: [], tasks: [] };
  }
  return JSON.parse(raw);
};

const saveDb = (db: MockDb) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
};

const delay = () => new Promise((resolve) => setTimeout(resolve, DELAY_MS));

export const mockTaskApi = {
  // STRICTLY MATCHES Task2ApiClient.getTasks signature (Promise<Task[]>)
  async getTasks(params?: any): Promise<Task[]> {
    await delay();
    const db = getDb();
    let items = [...db.tasks];

    // Simple filtering
    if (params?.project_id) {
        items = items.filter(t => t.primary_project === params.project_id);
    }
    if (params?.sprint_id) {
        items = items.filter(t => t.primary_sprint === params.sprint_id);
    }

    // Return array directly, mirroring Task2ApiClient behavior
    return items;
  },

  async createTask(payload: Partial<Task>): Promise<Task> {
    await delay();
    const db = getDb();

    const newTask: Task = {
        id: payload.id || `T-${Date.now()}`,
        title: payload.title || "New Task",
        description: payload.description || "",
        status: (payload.status as TaskStatus) || "new",
        priority: payload.priority || "medium",
        task_type: payload.task_type || "task",
        primary_project: payload.primary_project || "P-default",
        primary_sprint: payload.primary_sprint,
        parent_task_id: payload.parent_task_id,
        owner: payload.owner || "mock-user",
        // Required fields by strict schema (snake_case)
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        // Add defaults for fields to prevent UI crashes
        tags: [],
        comments: [],
        metadata: {},
        mission: "",
        goal: "",
        ...payload
    } as Task;

    db.tasks.push(newTask);
    saveDb(db);
    return newTask;
  },

  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    await delay();
    const db = getDb();
    const idx = db.tasks.findIndex(t => t.id === taskId);
    if (idx === -1) throw new Error("Task not found");

    const updated = {
        ...db.tasks[idx],
        ...updates,
        updated_at: new Date().toISOString()
    };

    db.tasks[idx] = updated;
    saveDb(db);
    return updated;
  },

  async getProjects(): Promise<Project[]> {
    await delay();
    const db = getDb();
    return db.projects;
  },

  async createProject(payload: Partial<Project>): Promise<Project> {
    await delay();
    const db = getDb();
    const newProject: Project = {
        id: payload.id || `P-${Date.now()}`,
        name: payload.name || "New Project",
        description: payload.description || "",
        status: payload.status || "active",
        owner: payload.owner || "mock-user",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        mission: payload.mission || "",
        vision: "",
        ...payload
    } as Project;

    db.projects.push(newProject);
    saveDb(db);
    return newProject;
  },

  async getSprints(projectId?: string): Promise<Sprint[]> {
    await delay();
    const db = getDb();
    let items = db.sprints;
    if (projectId) {
        items = items.filter(s => s.primary_project === projectId);
    }
    return items;
  },

  async createSprint(payload: Partial<Sprint>): Promise<Sprint> {
    await delay();
    const db = getDb();
    const newSprint: Sprint = {
        id: payload.id || `S-${Date.now()}`,
        name: payload.name || "New Sprint",
        goal: payload.goal || "",
        status: payload.status || "planning",
        primary_project: payload.primary_project || "P-default",
        start_date: payload.start_date || new Date().toISOString(),
        end_date: payload.end_date || new Date(Date.now() + 14 * 86400000).toISOString(),
        owner: payload.owner || "mock-user",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        ...payload
    } as Sprint;

    db.sprints.push(newSprint);
    saveDb(db);
    return newSprint;
  },

  // Helper to clear db
  resetDb: () => {
    localStorage.removeItem(STORAGE_KEY);
    toast.success("Mock Database Reset");
    window.location.reload();
  }
};
