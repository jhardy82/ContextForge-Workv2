import { Button } from '@/components/ui/button';
import { generateTask } from '@/mocks/data-generator';
import { RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { TaskDetailPanel } from './TaskDetailPanel';

export function DetailDemo() {
  const [task, setTask] = useState(() => generateTask());

  const handleRefresh = () => {
    setTask(generateTask());
  };

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
        {/* Sidebar Simulator */}
        <div className="w-16 border-r bg-muted/5 flex flex-col items-center py-4 gap-4">
             <div className="w-10 h-10 rounded bg-cyan-600/20 border border-cyan-500/50" />
             <Button variant="ghost" size="icon" onClick={handleRefresh} title="Generate New Task">
                <RefreshCw className="w-5 h-5" />
             </Button>
        </div>

        {/* Main Content Area (Background) */}
        <div className="flex-1 bg-black/20 p-8 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
                <h1 className="text-2xl font-bold mb-2">Detail Panel Demo</h1>
                <p>Verify 64-Field Rendering & Progressive Disclosure</p>
                <p className="text-sm opacity-50 mt-4">Task ID: {task.id}</p>
            </div>
        </div>

        {/* The Panel Itself */}
        <TaskDetailPanel
            task={task}
            onClose={() => console.log('Close clicked')}
            onEdit={(t) => console.log('Edit clicked', t)}
        />
    </div>
  );
}
