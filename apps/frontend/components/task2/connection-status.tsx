import { AlertCircle, CheckCircle, Loader2, WifiOff } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { ConnectionStatus as ConnectionStatusType } from '@/lib/types';

interface ConnectionStatusProps {
  status: ConnectionStatusType;
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export default function ConnectionStatus({ status, onRefresh, isRefreshing = false }: ConnectionStatusProps) {
  const getStatusIcon = () => {
    if (isRefreshing) return <Loader2 className="h-4 w-4 animate-spin" />;

    switch (status.status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'connecting':
        return <Loader2 className="h-4 w-4 animate-spin text-yellow-600" />;
      case 'disconnected':
        return <WifiOff className="h-4 w-4 text-gray-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <WifiOff className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    if (isRefreshing) return 'Refreshing...';

    switch (status.status) {
      case 'connected':
        return 'TaskMan-v2 API Connected';
      case 'connecting':
        return 'Connecting to TaskMan-v2 API...';
      case 'disconnected':
        return 'TaskMan-v2 API Disconnected (using sample data)';
      case 'error':
        return 'TaskMan-v2 API Error';
      default:
        return 'Unknown Status';
    }
  };

  const getVariant = () => {
    switch (status.status) {
      case 'connected':
        return 'default';
      case 'error':
        return 'destructive';
      default:
        return 'default';
    }
  };

  return (
    <Alert variant={getVariant()} className="mb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <AlertDescription className="mb-0">
            <div className="font-medium">{getStatusText()}</div>
            {status.message && (
              <div className="text-sm text-muted-foreground mt-1">
                {status.message}
              </div>
            )}
            {status.lastChecked && (
              <div className="text-xs text-muted-foreground mt-1">
                Last checked: {status.lastChecked.toLocaleTimeString()}
              </div>
            )}
          </AlertDescription>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={isRefreshing}
          className="ml-4"
        >
          {isRefreshing ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            'Refresh'
          )}
        </Button>
      </div>
    </Alert>
  );
}
