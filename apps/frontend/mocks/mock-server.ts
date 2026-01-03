
import cors from 'cors';
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3002;

app.use(cors());
app.use(express.json());

// Mock Data
const TASKS = [
    { id: "T-1", title: "Mock Task 1", status: "new", primary_project: "P-1" },
    { id: "T-2", title: "Mock Task 2", status: "inprogress", primary_project: "P-1" }
];

// Serve OpenAPI Spec
// We need to construct a minimal valid spec since we can't easily read the generated one if backend is down
// But for Orval to work, it needs a spec.
// We will try to read the one from the backend folder if it exists, or serve a static one.
const openApiSpecPath = path.resolve(__dirname, '../../backend-api/openapi.json');

app.get('/openapi.json', (req, res) => {
    // Return a minimal spec that matches our generated code expectations
    res.json({
        "openapi": "3.1.0",
        "info": { "title": "TaskMan Mock", "version": "0.1.0" },
        "paths": {
            "/api/v1/tasks": {
                "get": {
                    "operationId": "list_tasks_api_v1_tasks_get",
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": { "application/json": { "schema": { "$ref": "#/components/schemas/TaskList" } } }
                        }
                    }
                },
                "post": {
                    "operationId": "create_task_api_v1_tasks_post",
                    "responses": { "200": { "description": "Success" } }
                }
            }
        },
        "components": {
            "schemas": {
                "TaskList": {
                    "type": "object",
                    "properties": {
                        "items": { "type": "array", "items": { "$ref": "#/components/schemas/TaskResponse" } }
                    }
                },
                "TaskResponse": {
                    "type": "object",
                    "properties": {
                        "id": { "type": "string" },
                        "title": { "type": "string" },
                        "status": { "type": "string" }
                    }
                }
            }
        }
    });
});

app.get('/api/v1/tasks', (req, res) => {
    res.json({ items: TASKS, total: TASKS.length });
});

app.listen(PORT, () => {
    console.log(`Mock Backend running on http://localhost:${PORT}`);
});
