import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronRight } from 'lucide-react';
import React from 'react';

interface DetailSectionProps {
  title: string;
  icon?: React.ReactNode;
  defaultExpanded?: boolean;
  children: React.ReactNode;
  badge?: string | number;
  className?: string;
  tier?: 1 | 2 | 3;
}

export function DetailSection({
    title,
    icon,
    defaultExpanded = false,
    children,
    badge,
    className,
    tier = 2
}: DetailSectionProps) {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);

  return (
    <div className={cn("border rounded-md bg-card/30", className)}>
      <Button
        variant="ghost"
        className="w-full flex items-center justify-between p-3 h-auto hover:bg-accent/50 rounded-t-md rounded-b-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2 font-semibold text-sm">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          {title}
          {tier === 3 && (
              <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700 font-mono">
                  ADVANCED
              </span>
          )}
        </div>
        <div className="flex items-center gap-2">
            {badge && (
                <span className="text-xs bg-secondary px-2 py-0.5 rounded-full text-secondary-foreground">
                    {badge}
                </span>
            )}
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </div>
      </Button>

      {isExpanded && (
        <div className="p-3 border-t bg-black/10 animate-in slide-in-from-top-1 fade-in duration-200">
          {children}
        </div>
      )}
    </div>
  );
}

interface FieldGroupProps {
    children: React.ReactNode;
    className?: string;
}

export function FieldGroup({ children, className }: FieldGroupProps) {
    return <div className={cn("grid grid-cols-1 md:grid-cols-2 gap-4", className)}>{children}</div>;
}

interface FieldProps {
    label: string;
    value?: React.ReactNode;
    children?: React.ReactNode;
    className?: string;
}

export function Field({ label, value, children, className }: FieldProps) {
    return (
        <div className={cn("space-y-1", className)}>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                {label}
            </label>
            <div className="text-sm font-medium break-words min-h-[20px]">
                {children || value || <span className="text-muted-foreground/40 italic">Empty</span>}
            </div>
        </div>
    );
}

// NEW: Editable Field Wrapper
interface EditableFieldProps extends FieldProps {
    isEditing: boolean;
    fieldName?: string; // Key for the form
    onChange?: (value: string) => void;
    type?: 'text' | 'textarea' | 'number' | 'date' | 'select';
    options?: string[]; // For select
}

export function EditableField({
    isEditing,
    value,
    onChange,
    type = 'text',
    options,
    ...props
}: EditableFieldProps) {
    if (!isEditing) {
        return <Field {...props} value={value} />;
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        onChange?.(e.target.value);
    };

    let inputComponent;
    const stringValue = String(value ?? '');

    switch (type) {
        case 'textarea':
            inputComponent = <Textarea value={stringValue} onChange={handleChange} className="min-h-[80px]" />;
            break;
        case 'select':
            inputComponent = (
                <select
                    value={stringValue}
                    onChange={handleChange}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                    <option value="" disabled>Select...</option>
                    {options?.map(opt => (
                        <option key={opt} value={opt} className="bg-slate-900">{opt}</option>
                    ))}
                </select>
            );
            break;
        default:
            inputComponent = <Input type={type} value={stringValue} onChange={handleChange} />;
    }

    return (
        <div className={cn("space-y-1", props.className)}>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                {props.label}
            </label>
            {inputComponent}
        </div>
    );
}
