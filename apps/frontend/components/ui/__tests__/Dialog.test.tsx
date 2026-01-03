/**
 * CF-130 Phase 1.2: Dialog Component Tests
 * Tests for Dialog component behavior, accessibility, and subcomponents.
 */

import { fireEvent, render, screen, waitFor } from '@/test/utils/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { Button } from '../button'
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '../dialog'

describe('Dialog', () => {
  describe('Basic rendering', () => {
    it('does not render content when closed', () => {
      render(
        <Dialog>
          <DialogTrigger>Open</DialogTrigger>
          <DialogContent>
            <DialogTitle>Dialog Title</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument()
    })

    it('renders content when open', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Open Dialog</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByText('Open Dialog')).toBeInTheDocument()
    })

    it('has data-slot attribute on root', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Test</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByRole('dialog')).toHaveAttribute('data-slot', 'dialog-content')
    })
  })

  describe('DialogTrigger', () => {
    it('opens dialog when trigger clicked', async () => {
      render(
        <Dialog>
          <DialogTrigger asChild>
            <Button>Open Dialog</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogTitle>Triggered Dialog</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.queryByText('Triggered Dialog')).not.toBeInTheDocument()

      fireEvent.click(screen.getByRole('button', { name: /open dialog/i }))

      await waitFor(() => {
        expect(screen.getByText('Triggered Dialog')).toBeInTheDocument()
      })
    })

    it('has data-slot attribute', () => {
      render(
        <Dialog>
          <DialogTrigger>Trigger</DialogTrigger>
          <DialogContent>
            <DialogTitle>Title</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByText('Trigger')).toHaveAttribute('data-slot', 'dialog-trigger')
    })
  })

  describe('DialogContent', () => {
    it('renders content with overlay', () => {
      render(
        <Dialog open>
          <DialogContent data-testid="dialog-content">
            <DialogTitle>Content Test</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      const content = screen.getByTestId('dialog-content')
      expect(content).toBeInTheDocument()
    })

    it('renders close button', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>With Close</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument()
    })

    it('applies custom className', () => {
      render(
        <Dialog open>
          <DialogContent className="custom-dialog">
            <DialogTitle>Custom Class</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveClass('custom-dialog')
    })
  })

  describe('DialogHeader', () => {
    it('renders header section', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Header Title</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      )

      const header = screen.getByText('Header Title').parentElement
      expect(header).toHaveAttribute('data-slot', 'dialog-header')
    })

    it('has flex column layout', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogHeader data-testid="dialog-header">
              <DialogTitle>Flex Header</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      )

      const header = screen.getByTestId('dialog-header')
      expect(header).toHaveClass('flex')
      expect(header).toHaveClass('flex-col')
    })
  })

  describe('DialogTitle', () => {
    it('renders title text', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>My Dialog Title</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      const title = screen.getByText('My Dialog Title')
      expect(title).toBeInTheDocument()
      expect(title).toHaveAttribute('data-slot', 'dialog-title')
    })

    it('has correct typography styles', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Styled Title</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      const title = screen.getByText('Styled Title')
      expect(title).toHaveClass('text-lg')
      expect(title).toHaveClass('font-semibold')
    })
  })

  describe('DialogDescription', () => {
    it('renders description text', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Title</DialogTitle>
            <DialogDescription>This is a description</DialogDescription>
          </DialogContent>
        </Dialog>
      )

      const description = screen.getByText('This is a description')
      expect(description).toBeInTheDocument()
      expect(description).toHaveAttribute('data-slot', 'dialog-description')
    })

    it('has muted text styling', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Title</DialogTitle>
            <DialogDescription>Muted description</DialogDescription>
          </DialogContent>
        </Dialog>
      )

      const description = screen.getByText('Muted description')
      expect(description).toHaveClass('text-muted-foreground')
      expect(description).toHaveClass('text-sm')
    })
  })

  describe('DialogFooter', () => {
    it('renders footer section', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Title</DialogTitle>
            <DialogFooter data-testid="dialog-footer">
              <Button>Cancel</Button>
              <Button>Confirm</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )

      const footer = screen.getByTestId('dialog-footer')
      expect(footer).toHaveAttribute('data-slot', 'dialog-footer')
    })

    it('has flex layout for buttons', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Title</DialogTitle>
            <DialogFooter data-testid="dialog-footer">
              <Button>Action</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )

      const footer = screen.getByTestId('dialog-footer')
      expect(footer).toHaveClass('flex')
    })
  })

  describe('DialogClose', () => {
    it('closes dialog when clicked', async () => {
      const onOpenChange = vi.fn()
      render(
        <Dialog open onOpenChange={onOpenChange}>
          <DialogContent>
            <DialogTitle>Closable Dialog</DialogTitle>
            <DialogClose asChild>
              <Button>Close Me</Button>
            </DialogClose>
          </DialogContent>
        </Dialog>
      )

      fireEvent.click(screen.getByRole('button', { name: /close me/i }))

      await waitFor(() => {
        expect(onOpenChange).toHaveBeenCalledWith(false)
      })
    })

    it('has data-slot attribute', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Title</DialogTitle>
            <DialogClose>Close Dialog</DialogClose>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByText('Close Dialog')).toHaveAttribute('data-slot', 'dialog-close')
    })
  })

  describe('Complete Dialog composition', () => {
    it('renders full dialog structure', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirm Action</DialogTitle>
              <DialogDescription>
                Are you sure you want to proceed?
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">Cancel</Button>
              </DialogClose>
              <Button>Confirm</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByText('Confirm Action')).toBeInTheDocument()
      expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has dialog role', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Accessible Dialog</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('associates title with dialog', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Labeled Dialog</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      const dialog = screen.getByRole('dialog')
      const title = screen.getByText('Labeled Dialog')

      // Radix UI associates title via aria-labelledby
      expect(dialog).toHaveAttribute('aria-labelledby')
      expect(title).toBeInTheDocument()
    })

    it('has close button with accessible name', () => {
      render(
        <Dialog open>
          <DialogContent>
            <DialogTitle>Dialog</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      // The close button should have sr-only text "Close"
      const closeButton = screen.getByRole('button', { name: /close/i })
      expect(closeButton).toBeInTheDocument()
    })

    it('closes on escape key', async () => {
      const onOpenChange = vi.fn()
      render(
        <Dialog open onOpenChange={onOpenChange}>
          <DialogContent>
            <DialogTitle>Escape Dialog</DialogTitle>
          </DialogContent>
        </Dialog>
      )

      fireEvent.keyDown(document, { key: 'Escape' })

      await waitFor(() => {
        expect(onOpenChange).toHaveBeenCalledWith(false)
      })
    })
  })
})
