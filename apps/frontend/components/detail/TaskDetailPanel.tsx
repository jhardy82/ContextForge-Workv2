import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Task } from '@/types/objects';
import { format } from 'date-fns';
import {
    Activity,
    Briefcase,
    Calendar,
    Code2,
    GitBranch,
    Layers,
    LayoutGrid,
    PenLine,
    Save,
    ShieldCheck,
    Trash2,
    Users,
    X
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { DetailSection, EditableField, Field, FieldGroup } from './DetailSections';

interface TaskDetailPanelProps {
  task: Task | null;
  onClose?: () => void;
  onSave?: (taskId: string, updates: Partial<Task>) => Promise<void>;
  onDelete?: (taskId: string) => Promise<void>;
}

export function TaskDetailPanel({ task, onClose, onSave, onDelete }: TaskDetailPanelProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Task>>({});
  const [isSaving, setIsSaving] = useState(false);

  // Sync form with task when task changes
  useEffect(() => {
    if (task) {
        setEditForm({ ...task });
        setIsEditing(false);
    }
  }, [task?.id]); // Only reset on ID change, not every update to prevent forcing reset while typing

  if (!task) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground bg-muted/5 border-l">
        <div className="text-center">
            <LayoutGrid className="w-12 h-12 mx-auto mb-4 opacity-20" />
            <p>Select a task to view details</p>
        </div>
      </div>
    );
  }

  const handleFieldChange = (field: keyof Task, value: any) => {
      setEditForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
      if (!onSave) return;
      setIsSaving(true);
      try {
          await onSave(task.id, editForm);
          setIsEditing(false);
      } catch (error) {
          console.error("Failed to save task:", error);
      } finally {
          setIsSaving(false);
      }
  };

  const handleDelete = async () => {
    if (!onDelete || !task) return;
    if (confirm("Are you sure you want to delete this task?")) {
        await onDelete(task.id);
    }
  };

  const handleCancel = () => {
      setEditForm({ ...task });
      setIsEditing(false);
  };

  return (
    <div className="h-full flex flex-col bg-background border-l w-full max-w-2xl shadow-xl">
      {/* TIER 1: HEADER (Always Visible) */}
      <div className="p-6 border-b bg-card">
        <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline" className="font-mono text-xs text-muted-foreground">
                        {task.task_id}
                    </Badge>

                    {isEditing ? (
                        <>
                            <EditableField
                                isEditing={true}
                                label=""
                                value={editForm.status}
                                onChange={v => handleFieldChange('status', v)}
                                type="select"
                                options={['todo', 'in_progress', 'review', 'done', 'blocked']}
                                className="w-[120px]"
                            />
                            <EditableField
                                isEditing={true}
                                label=""
                                value={editForm.priority}
                                onChange={v => handleFieldChange('priority', v)}
                                type="select"
                                options={['critical', 'high', 'medium', 'low']}
                                className="w-[100px]"
                            />
                        </>
                    ) : (
                        <>
                            <Badge variant={task.status === 'done' ? 'default' : 'secondary'} className="uppercase">
                                {task.status}
                            </Badge>
                            <Badge variant={
                                task.priority === 'critical' ? 'destructive' :
                                task.priority === 'high' ? 'outline' : 'secondary'
                            } className={task.priority === 'high' ? 'border-orange-500 text-orange-500' : ''}>
                                {task.priority}
                            </Badge>
                        </>
                    )}
                </div>

                {isEditing ? (
                    <EditableField
                        isEditing={true}
                        label=""
                        value={editForm.title}
                        onChange={v => handleFieldChange('title', v)}
                        className="w-full text-xl font-bold"
                    />
                ) : (
                    <h2 className="text-2xl font-bold leading-tight">{task.title}</h2>
                )}
            </div>

            <div className="flex items-start gap-2">
                {isEditing ? (
                    <>
                        <Button size="sm" onClick={handleSave} disabled={isSaving} className="bg-green-600 hover:bg-green-700" aria-label="Save Task" data-testid="save-task-button">
                            <Save className="w-4 h-4 mr-2" />
                            {isSaving ? 'Saving...' : 'Save'}
                        </Button>
                        <Button size="sm" variant="outline" onClick={handleCancel} disabled={isSaving} aria-label="Cancel Edit" data-testid="cancel-edit-button">
                            <X className="w-4 h-4" />
                        </Button>
                    </>
                ) : (
                    <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)} aria-label="Edit Task" data-testid="edit-task-button">
                        <PenLine className="w-4 h-4" />
                    </Button>
                )}
                {onDelete && !isEditing && (
                    <Button variant="ghost" size="sm" onClick={handleDelete} className="text-red-400 hover:text-red-300 hover:bg-red-950/50" aria-label="Delete Task">
                        <Trash2 className="w-4 h-4" />
                    </Button>
                )}
                {onClose && (
                    <Button variant="ghost" size="icon" onClick={onClose} className="shrink-0 text-muted-foreground" aria-label="Close Panel" data-testid="close-panel-button">
                        ×
                    </Button>
                )}
            </div>
        </div>

        {/* Primary Metadata */}
        <div className="grid grid-cols-4 gap-4 text-sm mt-4">
             <EditableField
                isEditing={isEditing}
                label="Assignee"
                value={isEditing ? editForm.assignee : task.assignee}
                onChange={v => handleFieldChange('assignee', v)}
             />
             <EditableField
                isEditing={isEditing}
                label="Due Date"
                value={isEditing ? (editForm.due_date?.split('T')[0] || '') : (task.due_date ? format(new Date(task.due_date), 'MMM d, yyyy') : '-')}
                type="date"
                onChange={v => handleFieldChange('due_date', new Date(v).toISOString())}
             />
             <EditableField
                isEditing={isEditing}
                label="Effort"
                value={isEditing ? editForm.effort_estimate : `${task.effort_estimate} pts`}
                type="number"
                onChange={v => handleFieldChange('effort_estimate', Number(v))}
             />
             <Field label="Health">
                <div className={`flex items-center gap-1.5 ${
                    task.health === 'on_track' ? 'text-emerald-400' :
                    task.health === 'at_risk' ? 'text-yellow-400' : 'text-red-400'
                }`}>
                    <Activity className="w-3 h-3" />
                    <span className="capitalize">{task.health.replace('_', ' ')}</span>
                </div>
             </Field>
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        <div className="space-y-6 max-w-3xl mx-auto pb-10">

            {/* TIER 2: CORE CONTEXT (Collapsible) */}

            {/* Description */}
            <div className="prose prose-invert max-w-none">
                <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-2">Description</h3>
                {isEditing ? (
                    <EditableField
                        isEditing={true}
                        label=""
                        value={editForm.description}
                        onChange={v => handleFieldChange('description', v)}
                        type="textarea"
                    />
                ) : (
                    <div className="p-4 rounded-md bg-muted/30 text-sm leading-relaxed whitespace-pre-wrap border border-transparent hover:border-border transition-colors">
                        {task.description}
                    </div>
                )}
            </div>

            <Separator />

            <div className="grid gap-4">
                <DetailSection title="People & Resources" icon={<Users className="w-4 h-4" />}>
                     <FieldGroup>
                        <EditableField isEditing={isEditing} label="Reporter" value={isEditing ? editForm.reporter : task.reporter} onChange={v => handleFieldChange('reporter', v)} />
                        {/* Stakeholders would use a MultiSelect in future, simple text for now */}
                        <EditableField isEditing={isEditing} label="Complexity" value={isEditing ? editForm.complexity : task.complexity?.toUpperCase()} onChange={v => handleFieldChange('complexity', v)} />
                     </FieldGroup>
                </DetailSection>

                <DetailSection title="Planning & Relationships" icon={<GitBranch className="w-4 h-4" />}>
                     <FieldGroup>
                        <EditableField isEditing={isEditing} label="Project" value={isEditing ? editForm.project_id : (task.project_id || 'None')} onChange={v => handleFieldChange('project_id', v)} />
                        <EditableField isEditing={isEditing} label="Sprint" value={isEditing ? editForm.sprint_id : (task.sprint_id || 'Backlog')} onChange={v => handleFieldChange('sprint_id', v)} />
                        <EditableField isEditing={isEditing} label="Parent Task" value={isEditing ? editForm.parent_task_id : (task.parent_task_id || 'None')} onChange={v => handleFieldChange('parent_task_id', v)} />
                        <EditableField isEditing={isEditing} label="Epic" value={isEditing ? editForm.epic_id : (task.epic_id || 'None')} onChange={v => handleFieldChange('epic_id', v)} />
                     </FieldGroup>
                </DetailSection>

                <DetailSection title="Time Tracking" icon={<Calendar className="w-4 h-4" />} defaultExpanded>
                     <FieldGroup>
                        <Field label="Created" value={format(new Date(task.created_at), 'MMM d, h:mm a')} />
                        <Field label="Updated" value={format(new Date(task.updated_at), 'MMM d, h:mm a')} />
                     </FieldGroup>
                     <div className="mt-4 grid grid-cols-3 gap-2 bg-black/20 p-2 rounded">
                        <EditableField isEditing={isEditing} label="Est" value={isEditing ? editForm.estimated_hours : `${task.estimated_hours || 0}h`} type="number" onChange={v => handleFieldChange('estimated_hours', Number(v))} className="text-center" />
                        <EditableField isEditing={isEditing} label="Act" value={isEditing ? editForm.actual_hours : `${task.actual_hours || 0}h`} type="number" onChange={v => handleFieldChange('actual_hours', Number(v))} className="text-center" />
                        <EditableField isEditing={isEditing} label="Rem" value={isEditing ? editForm.remaining_hours : `${task.remaining_hours || 0}h`} type="number" onChange={v => handleFieldChange('remaining_hours', Number(v))} className="text-center" />
                     </div>
                </DetailSection>
            </div>

            {/* TIER 3: ADVANCED MODE TOGGLE */}
            <div className="flex items-center justify-between py-6">
                <div className="h-px flex-1 bg-border" />
                <div className="px-4 flex items-center gap-3">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Advanced Context</span>
                    <Switch checked={showAdvanced} onCheckedChange={setShowAdvanced} />
                </div>
                <div className="h-px flex-1 bg-border" />
            </div>

            {/* TIER 3: ADVANCED SECTIONS */}
            {showAdvanced && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">

                    <DetailSection title="Business Context" icon={<Briefcase className="w-4 h-4" />} tier={3}>
                        <FieldGroup>
                            <EditableField isEditing={isEditing} label="Business Value" value={isEditing ? editForm.business_value : task.business_value} type="number" onChange={v => handleFieldChange('business_value', Number(v))} />
                            <EditableField isEditing={isEditing} label="ROI Score" value={isEditing ? editForm.roi_score : (task.roi_score || '-')} type="number" onChange={v => handleFieldChange('roi_score', Number(v))} />
                            <EditableField isEditing={isEditing} label="Strat Alignment" value={isEditing ? editForm.strategic_alignment : `${task.strategic_alignment}/10`} type="number" onChange={v => handleFieldChange('strategic_alignment', Number(v))} />
                            <EditableField isEditing={isEditing} label="Customer Impact" value={isEditing ? editForm.customer_impact : task.customer_impact.toUpperCase()} onChange={v => handleFieldChange('customer_impact', v)} />
                        </FieldGroup>
                    </DetailSection>

                    <DetailSection title="Technical Details" icon={<Code2 className="w-4 h-4" />} tier={3}>
                        <FieldGroup>
                            <EditableField isEditing={isEditing} label="Tech Scope" value={isEditing ? editForm.technical_scope : task.technical_scope} onChange={v => handleFieldChange('technical_scope', v)} />
                            <EditableField isEditing={isEditing} label="Deployment" value={isEditing ? editForm.deployment_env : task.deployment_env.toUpperCase()} onChange={v => handleFieldChange('deployment_env', v)} />
                            <EditableField isEditing={isEditing} label="Tech Debt" value={isEditing ? editForm.tech_debt_score : `${task.tech_debt_score}/10`} type="number" onChange={v => handleFieldChange('tech_debt_score', Number(v))} />
                        </FieldGroup>
                    </DetailSection>

                   <DetailSection title="Quality & Validation" icon={<ShieldCheck className="w-4 h-4" />} tier={3}>
                        <div className="grid grid-cols-2 gap-4 mb-4">
                             <div className="bg-muted/20 p-3 rounded flex items-center justify-between">
                                <span className="text-xs font-medium">Test Coverage</span>
                                {isEditing ? (
                                    <EditableField isEditing={true} label="" value={editForm.test_coverage} type="number" onChange={v => handleFieldChange('test_coverage', Number(v))} />
                                ) : (
                                    <span className={task.test_coverage < 80 ? 'text-red-400' : 'text-green-400'}>
                                        {task.test_coverage}%
                                    </span>
                                )}
                             </div>
                             <div className="bg-muted/20 p-3 rounded flex items-center justify-between">
                                <span className="text-xs font-medium">Security Audit</span>
                                <Badge variant={task.security_audit_status === 'passed' ? 'outline' : 'secondary'}>
                                    {task.security_audit_status}
                                </Badge>
                             </div>
                        </div>
                    </DetailSection>

                    <DetailSection title="COF Dimensions" icon={<Layers className="w-4 h-4 text-purple-400" />} tier={3}>
                         {/* Edit mode for COF not fully implemented for brevity, just visualization */}
                         <div className="grid grid-cols-4 gap-2 text-center">
                            {[
                                { l: 'Motiv', v: task.cof_motivational },
                                { l: 'Relat', v: task.cof_relational },
                                { l: 'Situa', v: task.cof_situational },
                                { l: 'Tempo', v: task.cof_temporal },
                            ].map(d => (
                                <div key={d.l} className="bg-purple-900/20 p-2 rounded border border-purple-500/20">
                                    <div className="text-[10px] text-purple-300 mb-1">{d.l}</div>
                                    <div className="font-bold">{d.v}</div>
                                </div>
                            ))}
                         </div>
                    </DetailSection>

                </div>
            )}

            <div className="h-10" /> {/* Bottom padding */}
        </div>
      </ScrollArea>
    </div>
  );
}
