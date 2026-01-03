import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { TaskPriority, TaskStatus } from "../../core/types.js";
import { logger } from "../../infrastructure/logger.js";

const parseTaskInputSchema = z.object({
  input: z.string().min(1, "Input text is required"),
});

const parsedTaskSchema = z.object({
  title: z.string(),
  priority: z.nativeEnum(TaskPriority).optional(),
  status: z.nativeEnum(TaskStatus).optional(),
  tags: z.array(z.string()).optional(),
  confidence: z.number().min(0).max(1),
});

export function parseTaskLogic(
  input: string
): z.infer<typeof parsedTaskSchema> {
  let title = input;
  let priority: TaskPriority | undefined;
  let status: TaskStatus | undefined;
  const tags: string[] = [];

  // Priority detection
  const priorityMap: Record<string, TaskPriority> = {
    p1: TaskPriority.High,
    high: TaskPriority.High,
    urgent: TaskPriority.High,
    critical: TaskPriority.Critical,
    p2: TaskPriority.Medium,
    medium: TaskPriority.Medium,
    normal: TaskPriority.Medium,
    p3: TaskPriority.Low,
    low: TaskPriority.Low,
  };

  // Status detection
  const statusMap: Record<string, TaskStatus> = {
    todo: TaskStatus.New,
    doing: TaskStatus.InProgress,
    "in progress": TaskStatus.InProgress,
    review: TaskStatus.Pending,
    done: TaskStatus.Completed,
    completed: TaskStatus.Completed,
    blocked: TaskStatus.Blocked,
  };

  // Extract tags (#tag)
  const tagRegex = /#(\w+)/g;
  const tagMatches = input.match(tagRegex);
  if (tagMatches) {
    tags.push(...tagMatches.map((t) => t.substring(1)));
    title = title.replace(tagRegex, "").trim();
  }

  // Extract priority
  const priorityMatch = title.match(
    /\b(priority|p)[:\s]+(high|medium|low|urgent|critical|p1|p2|p3)\b/i
  );
  if (priorityMatch) {
    const key = priorityMatch[2].toLowerCase();
    priority = priorityMap[key];
    title = title.replace(priorityMatch[0], "").trim();
  }

  // Extract status
  const statusMatch = title.match(
    /\b(status)[:\s]+(todo|doing|in progress|review|done|completed|blocked)\b/i
  );
  if (statusMatch) {
    const key = statusMatch[2].toLowerCase();
    status = statusMap[key];
    title = title.replace(statusMatch[0], "").trim();
  }

  // Clean up
  title = title.replace(/\s+/g, " ").trim();

  return {
    title,
    priority,
    status,
    tags: tags.length > 0 ? tags : undefined,
    confidence: 0.8, // Static confidence for regex
  };
}

export function registerAiFeatures(server: McpServer): void {
  server.registerTool(
    "ai_parse_task",
    {
      title: "Parse Task Natural Language",
      description:
        "Parse natural language text into a structured task object using internal logic.",
      inputSchema: parseTaskInputSchema.shape,
      outputSchema: {
        parsed: parsedTaskSchema,
      },
    },
    async ({ input }) => {
      logger.debug({ input }, "Parsing natural language task input");
      const parsed = parseTaskLogic(input);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(parsed),
          },
        ],
        structuredContent: { parsed },
      };
    }
  );
}
