import { useState } from 'react';
import { Copy, ExternalLink, MessageSquare } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Task, AI_PROMPT_TYPES, SACRED_GEOMETRY_SHAPES, STATUS_COLORS } from '@/lib/types';
import { Task2ApiClient } from '@/lib/task2-api';
import { cn } from '@/lib/utils';

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  apiClient: Task2ApiClient;
}

export default function TaskDetailModal({ task, isOpen, onClose, apiClient }: TaskDetailModalProps) {
  const [generatedPrompts, setGeneratedPrompts] = useState<Record<string, string>>({});

  if (!task) return null;

  const handleCopyField = (fieldName: string, value: string) => {
    navigator.clipboard.writeText(value);
    toast.success(`Copied ${fieldName} to clipboard`);
  };

  const handleCopyFullTask = () => {
    const taskJson = JSON.stringify(task, null, 2);
    navigator.clipboard.writeText(taskJson);
    toast.success('Copied full task JSON to clipboard');
  };

  const handleGeneratePrompt = (type: 'implementation' | 'testing' | 'validation') => {
    const prompt = apiClient.generateAIPrompt(task, type);
    setGeneratedPrompts(prev => ({ ...prev, [type]: prompt }));
    toast.info(`Generated ${type} prompt`);
  };

  const handleSendToChat = (prompt: string, type: string) => {
    // In a real implementation, this would integrate with VS Code Chat or GitHub Copilot
    console.log(`Sending ${type} prompt to chat:`, prompt);
    navigator.clipboard.writeText(prompt);
    toast.success(`Copied ${type} prompt to clipboard - paste in your AI chat interface`);
  };

  const shapeIcon = task.shape ? SACRED_GEOMETRY_SHAPES[task.shape] : '📋';
  const statusColor = STATUS_COLORS[task.status];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span className="text-2xl">{shapeIcon}</span>
            <div>
              <div className="font-mono text-sm text-muted-foreground">{task.id}</div>
              <div>{task.title}</div>
            </div>
          </DialogTitle>
          <DialogDescription>
            Task details and AI prompt generation
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-6">
            {/* Status and metadata */}
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant="outline"
                className={cn(
                  "flex items-center gap-1",
                  `text-${statusColor}`
                )}
              >
                <div className={cn("w-2 h-2 rounded-full", `bg-${statusColor}`)} />
                {task.status.replace('_', ' ')}
              </Badge>

              {task.priority && (
                <Badge variant="secondary">
                  Priority: {task.priority}
                </Badge>
              )}

              {task.shape && (
                <Badge variant="outline">
                  {shapeIcon} {task.shape}
                </Badge>
              )}

              {task.project_id && (
                <Badge variant="outline">
                  Project: {task.project_id}
                </Badge>
              )}
            </div>

            {/* Description */}
            {task.description && (
              <div>
                <h3 className="font-medium mb-2">Description</h3>
                <div className="p-3 bg-muted rounded-md">
                  <p className="text-sm whitespace-pre-wrap">{task.description}</p>
                </div>
              </div>
            )}

            {/* AI Prompt Generation */}
            <div>
              <h3 className="font-medium mb-4">AI Assistance</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {AI_PROMPT_TYPES.map(({ type, label, icon }) => (
                  <div key={type} className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => handleGeneratePrompt(type)}
                    >
                      <span className="mr-2">{icon}</span>
                      Generate {label} Prompt
                    </Button>

                    {generatedPrompts[type] && (
                      <div className="space-y-2">
                        <div className="p-3 bg-muted rounded-md text-xs font-mono">
                          <div className="max-h-32 overflow-y-auto">
                            {generatedPrompts[type]}
                          </div>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="secondary"
                            className="flex-1"
                            onClick={() => handleSendToChat(generatedPrompts[type], label)}
                          >
                            <MessageSquare className="h-3 w-3 mr-1" />
                            Send to Chat
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleCopyField(`${label} prompt`, generatedPrompts[type])}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Raw task data */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium">Raw Task Data</h3>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleCopyFullTask}
                >
                  <Copy className="h-3 w-3 mr-1" />
                  Copy JSON
                </Button>
              </div>

              <div className="p-4 bg-muted rounded-md">
                <pre className="text-xs font-mono overflow-x-auto">
                  {JSON.stringify(task, null, 2)}
                </pre>
              </div>
            </div>

            {/* Individual field copy buttons */}
            <div>
              <h3 className="font-medium mb-2">Quick Copy Fields</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopyField('Task ID', task.id)}
                >
                  Copy ID
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopyField('Title', task.title)}
                >
                  Copy Title
                </Button>
                {task.description && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopyField('Description', task.description!)}
                  >
                    Copy Description
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopyField('Status', task.status)}
                >
                  Copy Status
                </Button>
              </div>
            </div>

            {/* Timestamps */}
            <div className="text-xs text-muted-foreground space-y-1">
              <div>Created: {new Date(task.created_at).toLocaleString()}</div>
              {task.updated_at && (
                <div>Updated: {new Date(task.updated_at).toLocaleString()}</div>
              )}
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
