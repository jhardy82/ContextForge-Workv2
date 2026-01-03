import { Skeleton } from '@/components/ui/skeleton';

export function TreeSkeleton() {
  return (
    <div className="space-y-2 p-2" role="progressbar" aria-label="Loading task tree">
      {Array.from({ length: 15 }).map((_, i) => (
        <div key={i} className="flex items-center gap-2" style={{ paddingLeft: `${(i % 3) * 20}px` }}>
          <Skeleton className="h-4 w-4 rounded" />
          <Skeleton className="h-6 w-full max-w-[300px]" />
          <div className="ml-auto flex gap-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-12" />
          </div>
        </div>
      ))}
    </div>
  );
}
