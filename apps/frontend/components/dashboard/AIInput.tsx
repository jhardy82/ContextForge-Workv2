import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Task, TaskPriority, TaskStatus } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ArrowRight, Sparkles, Tag } from "lucide-react";
import { useEffect, useState } from "react";

interface AIInputProps {
  onTaskCreate: (task: Partial<Task>) => void;
  className?: string;
}

interface ParsedResult {
  title: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  tags?: string[];
}

export function AIInput({ onTaskCreate, className }: AIInputProps) {
  const [input, setInput] = useState("");
  const [parsed, setParsed] = useState<ParsedResult | null>(null);
  const [isParsing, setIsParsing] = useState(false);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (input.trim()) {
        setIsParsing(true);
        try {
          const res = await fetch('http://localhost:3002/ai/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input })
          });
          if (res.ok) {
            const data = await res.json();
            setParsed(data);
          }
        } catch (error) {
          console.error("Failed to parse", error);
        } finally {
          setIsParsing(false);
        }
      } else {
        setParsed(null);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!parsed || !input.trim()) return;

    onTaskCreate({
      title: parsed.title,
      priority: parsed.priority || 'medium',
      status: parsed.status || 'todo',
    });

    setInput("");
    setParsed(null);
  };

  const priorityColor = (p?: TaskPriority) => {
    switch (p) {
      case 'high': return 'bg-red-500/10 text-red-600 border-red-500/20';
      case 'medium': return 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20';
      case 'low': return 'bg-blue-500/10 text-blue-600 border-blue-500/20';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className={cn("relative group", className)}>
      <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg opacity-30 group-hover:opacity-50 blur transition duration-500"></div>
      <form onSubmit={handleSubmit} className="relative bg-background rounded-lg border shadow-sm p-1 flex flex-col gap-2">
        <div className="flex items-center gap-2 pl-3">
          <Sparkles className={cn("w-5 h-5 transition-colors", input ? "text-purple-500" : "text-muted-foreground", isParsing && "animate-pulse")} />
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask AI to create a task... (e.g., 'Fix login bug priority high #bug')"
            className="border-none shadow-none focus-visible:ring-0 px-0 h-10 text-base"
          />
          <Button
            type="submit"
            size="sm"
            variant="ghost"
            disabled={!input.trim()}
            className="mr-1"
          >
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>

        {/* Parsed Preview Chips */}
        {parsed && (parsed.priority || parsed.status || parsed.tags) && (
          <div className="flex items-center gap-2 px-3 pb-2 animate-in fade-in slide-in-from-top-1">
            <div className="h-4 border-l mx-1 bg-border" />

            {parsed.priority && (
              <Badge variant="outline" className={priorityColor(parsed.priority)}>
                Priority: {parsed.priority}
              </Badge>
            )}

            {parsed.status && (
              <Badge variant="outline" className="bg-slate-500/10 text-slate-600 border-slate-500/20">
                Status: {parsed.status}
              </Badge>
            )}

            {parsed.tags?.map(tag => (
              <Badge key={tag} variant="secondary" className="gap-1 text-xs">
                <Tag className="w-3 h-3" />
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </form>
    </div>
  );
}
