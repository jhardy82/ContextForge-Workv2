import { cn } from '@/lib/utils';
import { useKV } from '@github/spark/hooks';
import { Image } from '@phosphor-icons/react';

interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps) {
  const [logoUrl] = useKV('logo-url', '')
  const [logoText] = useKV('logo-text', 'DTM Task Manager')
  const [showLogo] = useKV('show-logo', 'true')

  if (showLogo !== 'true') {
    return null
  }

  return (
    <div className={cn("flex items-center gap-3", className)}>
      {logoUrl ? (
        <img src={logoUrl} alt="Logo" className="h-8 w-auto" />
      ) : (
        <div className="h-8 w-8 rounded bg-primary/10 flex items-center justify-center">
          <Image className="h-4 w-4 text-primary" />
        </div>
      )}
      <span className="font-semibold text-lg">{logoText || 'DTM Task Manager'}</span>
    </div>
  )
}
