import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';
import { useQueryClient } from '@tanstack/react-query';
import { Database, LayoutGrid, Moon, Power, Sun, Trash2, Wifi } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

interface ApiConnection {
    id: string;
    name: string;
    url: string;
    type: 'localhost' | 'production' | 'custom';
    isActive: boolean;
    isDefault?: boolean;
}

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DEFAULT_CONNECTIONS: ApiConnection[] = [
    { id: 'local-docker', name: 'Local Docker', url: 'http://localhost:3001/api/v1', type: 'localhost', isActive: true, isDefault: true },
    { id: 'production', name: 'Production', url: 'https://api.taskman.app/v1', type: 'production', isActive: false, isDefault: true },
];

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const queryClient = useQueryClient();
  const [isDark, setIsDark] = useState(true);
  const [connections, setConnections] = useState<ApiConnection[]>([]);
  const [showAddConnection, setShowAddConnection] = useState(false);
  const [newConnectionName, setNewConnectionName] = useState('');
  const [newConnectionUrl, setNewConnectionUrl] = useState('');

  // Sync with document class and load connections
  useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains('dark');
    setIsDark(isDarkMode);

    // Load connections
    const stored = localStorage.getItem('taskman_connections');
    const storedActiveUrl = localStorage.getItem('taskman_api_url');

    if (stored) {
        let parsed = JSON.parse(stored) as ApiConnection[];
        // Sync active state with taskman_api_url if mismatch
        if (storedActiveUrl) {
            parsed = parsed.map(c => ({ ...c, isActive: c.url === storedActiveUrl }));
            // If no active found, maybe it was a custom one-off, or we just default to first
             if (!parsed.some(c => c.isActive)) {
                  // Fallback: create a custom entry for the unknown URL or just reset
                  // For now, let's just assume the first is active if none match
             }
        }
        setConnections(parsed);
    } else {
        // Init defaults
        const initial = DEFAULT_CONNECTIONS.map(c => ({
            ...c,
            isActive: c.url === (storedActiveUrl || 'http://localhost:3001/api/v1')
        }));
        setConnections(initial);
        localStorage.setItem('taskman_connections', JSON.stringify(initial));
    }
  }, [open]);

  const handleAddConnection = () => {
    const newConn: ApiConnection = {
        id: crypto.randomUUID(),
        name: newConnectionName,
        url: newConnectionUrl,
        type: 'custom',
        isActive: false
    };
    const updated = [...connections, newConn];
    setConnections(updated);
    localStorage.setItem('taskman_connections', JSON.stringify(updated));
    setShowAddConnection(false);
    setNewConnectionName('');
    setNewConnectionUrl('');
    toast.success('Connection added');
  };

  const handleDeleteConnection = (id: string) => {
    const updated = connections.filter(c => c.id !== id);
    setConnections(updated);
    localStorage.setItem('taskman_connections', JSON.stringify(updated));
    toast.success('Connection deleted');
  };

  const handleActivateConnection = (id: string) => {
    const target = connections.find(c => c.id === id);
    if (!target) return;

    const updated = connections.map(c => ({ ...c, isActive: c.id === id }));
    setConnections(updated);
    localStorage.setItem('taskman_connections', JSON.stringify(updated));

    // Critical: Update the key used by DashboardV3
    localStorage.setItem('taskman_api_url', target.url);

    toast.success(`Switched to ${target.name}`);
    window.location.reload();
  };

  const toggleTheme = (checked: boolean) => {
    setIsDark(checked);
    if (checked) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleClearCache = () => {
    queryClient.clear();
    toast.success('Local cache cleared');
    onOpenChange(false);
    window.location.reload();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-slate-900 border-white/10 text-white">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription className="text-slate-400">
            Customize your TaskMan experience and manage local data.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-6 py-4">

          {/* Appearance */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium text-slate-200">Appearance</h4>
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 p-4">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                    {isDark ? <Moon size={16} className="text-purple-400" /> : <Sun size={16} className="text-amber-400" />}
                    <Label className="text-base">Dark Mode</Label>
                </div>
                <p className="text-xs text-slate-400">
                  Toggle application theme
                </p>
              </div>
              <Switch checked={isDark} onCheckedChange={toggleTheme} />
            </div>
          </div>

          {/* Data Management */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium text-slate-200">Data Management</h4>
            {/* ... existing clear cache button ... */}
            <div className="flex items-center justify-between rounded-lg border border-red-500/20 bg-red-500/10 p-4">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                    <Trash2 size={16} className="text-red-400" />
                    <Label className="text-base text-red-100">Clear Cache</Label>
                </div>
                <p className="text-xs text-red-200/70">
                  Reset local state and reload
                </p>
              </div>
              <Button variant="destructive" size="sm" onClick={handleClearCache}>
                Reset
              </Button>
            </div>
          </div>

          {/* Connections (Phase 23) */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-slate-200">Connections</h4>
                <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => setShowAddConnection(true)}>
                    + Add New
                </Button>
            </div>

            <div className="space-y-2 rounded-lg border border-white/5 bg-white/5 p-4 max-h-[200px] overflow-y-auto">
                {connections.map(conn => (
                    <div key={conn.id} className={cn("flex items-center justify-between p-2 rounded border transition-colors",
                        conn.isActive ? "bg-cyan-500/10 border-cyan-500/30" : "bg-black/20 border-white/5 hover:border-white/10"
                    )}>
                        <div className="flex items-center gap-3 overflow-hidden">
                            {conn.type === 'localhost' ? <Wifi size={14} className={cn(conn.isActive ? "text-cyan-400" : "text-slate-500")} /> :
                             conn.type === 'production' ? <Database size={14} className={cn(conn.isActive ? "text-purple-400" : "text-slate-500")} /> :
                             <LayoutGrid size={14} className="text-slate-500" />}

                            <div className="flex flex-col min-w-0">
                                <span className={cn("text-sm font-medium truncate", conn.isActive ? "text-cyan-100" : "text-slate-300")}>
                                    {conn.name}
                                </span>
                                <span className="text-[10px] text-slate-500 truncate">{conn.url}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-1">
                            {!conn.isActive && (
                                <Button variant="ghost" size="icon" className="h-6 w-6 text-green-400 hover:text-green-300 hover:bg-green-400/10" title="Activate" onClick={() => handleActivateConnection(conn.id)}>
                                    <Power size={12} />
                                </Button>
                            )}
                            {!conn.isDefault && (
                                <Button variant="ghost" size="icon" className="h-6 w-6 text-slate-500 hover:text-red-400 hover:bg-red-400/10" onClick={() => handleDeleteConnection(conn.id)}>
                                    <Trash2 size={12} />
                                </Button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
          </div>

        {/* Add Connection Overlay */}
        {showAddConnection && (
            <div className="absolute inset-0 bg-slate-900/95 backdrop-blur-sm z-50 flex items-center justify-center p-6 rounded-lg animate-in fade-in duration-200">
                <div className="w-full space-y-4">
                    <h5 className="font-medium text-slate-200">Add New Connection</h5>
                    <div className="space-y-3">
                        <div className="space-y-1">
                            <Label className="text-xs">Name</Label>
                            <input
                                className="w-full bg-black/20 border border-white/10 rounded px-2 py-1.5 text-sm"
                                placeholder="e.g. Staging Server"
                                value={newConnectionName}
                                onChange={(e) => setNewConnectionName(e.target.value)}
                            />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">API URL</Label>
                            <input
                                className="w-full bg-black/20 border border-white/10 rounded px-2 py-1.5 text-sm"
                                placeholder="http://..."
                                value={newConnectionUrl}
                                onChange={(e) => setNewConnectionUrl(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="flex justify-end gap-2 pt-2">
                        <Button variant="ghost" size="sm" onClick={() => setShowAddConnection(false)}>Cancel</Button>
                        <Button size="sm" onClick={handleAddConnection} disabled={!newConnectionName || !newConnectionUrl}>Save</Button>
                    </div>
                </div>
            </div>
        )}

          {/* About */}
          <div className="pt-4 border-t border-white/10">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>TaskMan v3.0.0</span>
              <span>Build 2024.12.27</span>
            </div>
          </div>

        </div>
      </DialogContent>
    </Dialog>
  );
}
