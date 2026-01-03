import { Task } from '@/lib/types';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { TaskContextMenu } from '../TaskContextMenu';

// Mock TooltipProvider since it's often used in Radix primitives and can cause issues in tests if not wrapped
vi.mock('@/components/ui/tooltip', () => ({
  TooltipProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Tooltip: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  TooltipTrigger: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  TooltipContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

describe('TaskContextMenu', () => {
    const mockTask: Task = {
        id: '123',
        title: 'Test Task',
        status: 'todo',
        priority: 'medium',
        project_id: 'proj_1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
    };

    const mockHandlers = {
        onRunAIAction: vi.fn(),
        onDelete: vi.fn(),
        onDuplicate: vi.fn(),
        onStatusChange: vi.fn()
    };

    const renderComponent = () => {
        return render(
            <TaskContextMenu
                task={mockTask}
                onRunAIAction={mockHandlers.onRunAIAction}
                onDelete={mockHandlers.onDelete}
                onDuplicate={mockHandlers.onDuplicate}
                onStatusChange={mockHandlers.onStatusChange}
            >
                <div data-testid="task-card">Task Card Content</div>
            </TaskContextMenu>
        );
    };

    it('renders children correctly', () => {
        renderComponent();
        expect(screen.getByTestId('task-card')).toBeInTheDocument();
    });

    it('opens context menu on right click', async () => {
         renderComponent();
         const trigger = screen.getByTestId('task-card');

         // Trigger right click
         fireEvent.contextMenu(trigger);

         // Check if menu items are visible
         // Radix Context Menu renders in a portal, so we query globally
         await waitFor(() => {
             expect(screen.getByText('AI CONSTALLATION')).toBeInTheDocument();
             expect(screen.getByText('Auto-Breakdown Task')).toBeInTheDocument();
         });
    });

    it('triggers AI action when clicked', async () => {
        const user = userEvent.setup();
        renderComponent();
        const trigger = screen.getByTestId('task-card');
        fireEvent.contextMenu(trigger);

        await waitFor(() => expect(screen.getByText('Auto-Breakdown Task')).toBeInTheDocument());

        await user.click(screen.getByText('Auto-Breakdown Task'));
        expect(mockHandlers.onRunAIAction).toHaveBeenCalledWith('breakdown', mockTask);
    });

    it('triggers Duplicate action when clicked', async () => {
        const user = userEvent.setup();
        renderComponent();
        const trigger = screen.getByTestId('task-card');
        fireEvent.contextMenu(trigger);

        await waitFor(() => expect(screen.getByText('Duplicate')).toBeInTheDocument());

        await user.click(screen.getByText('Duplicate'));
        expect(mockHandlers.onDuplicate).toHaveBeenCalledWith(mockTask);
    });

    it('triggers Delete action when clicked', async () => {
        const user = userEvent.setup();
        renderComponent();
        const trigger = screen.getByTestId('task-card');
        fireEvent.contextMenu(trigger);

        await waitFor(() => expect(screen.getByText('Delete Task')).toBeInTheDocument());

        await user.click(screen.getByText('Delete Task'));
        expect(mockHandlers.onDelete).toHaveBeenCalledWith(mockTask.id);
    });
});
