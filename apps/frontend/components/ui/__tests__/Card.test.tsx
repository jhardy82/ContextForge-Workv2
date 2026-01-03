/**
 * CF-130 Phase 1.2: Card Component Tests
 * Tests for Card component and its subcomponents.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils/test-utils'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardAction,
} from '../card'

describe('Card', () => {
  describe('Card component', () => {
    it('renders card container', () => {
      render(<Card>Card content</Card>)
      const card = screen.getByText('Card content')
      expect(card).toBeInTheDocument()
      expect(card).toHaveAttribute('data-slot', 'card')
    })

    it('applies custom className', () => {
      render(<Card className="custom-card">Content</Card>)
      const card = screen.getByText('Content')
      expect(card).toHaveClass('custom-card')
    })

    it('has correct base styles', () => {
      render(<Card>Styled card</Card>)
      const card = screen.getByText('Styled card')
      expect(card).toHaveClass('bg-card')
      expect(card).toHaveClass('rounded-xl')
      expect(card).toHaveClass('border')
      expect(card).toHaveClass('shadow-sm')
    })
  })

  describe('CardHeader', () => {
    it('renders card header', () => {
      render(
        <Card>
          <CardHeader>Header content</CardHeader>
        </Card>
      )
      const header = screen.getByText('Header content')
      expect(header).toBeInTheDocument()
      expect(header).toHaveAttribute('data-slot', 'card-header')
    })

    it('applies grid layout', () => {
      render(
        <Card>
          <CardHeader>Grid header</CardHeader>
        </Card>
      )
      const header = screen.getByText('Grid header')
      expect(header).toHaveClass('grid')
    })
  })

  describe('CardTitle', () => {
    it('renders card title', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
        </Card>
      )
      const title = screen.getByText('Card Title')
      expect(title).toBeInTheDocument()
      expect(title).toHaveAttribute('data-slot', 'card-title')
    })

    it('has font-semibold styling', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Bold Title</CardTitle>
          </CardHeader>
        </Card>
      )
      const title = screen.getByText('Bold Title')
      expect(title).toHaveClass('font-semibold')
    })
  })

  describe('CardDescription', () => {
    it('renders card description', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Card description text</CardDescription>
          </CardHeader>
        </Card>
      )
      const description = screen.getByText('Card description text')
      expect(description).toBeInTheDocument()
      expect(description).toHaveAttribute('data-slot', 'card-description')
    })

    it('has muted text styling', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Muted description</CardDescription>
          </CardHeader>
        </Card>
      )
      const description = screen.getByText('Muted description')
      expect(description).toHaveClass('text-muted-foreground')
      expect(description).toHaveClass('text-sm')
    })
  })

  describe('CardContent', () => {
    it('renders card content', () => {
      render(
        <Card>
          <CardContent>Main content area</CardContent>
        </Card>
      )
      const content = screen.getByText('Main content area')
      expect(content).toBeInTheDocument()
      expect(content).toHaveAttribute('data-slot', 'card-content')
    })

    it('has horizontal padding', () => {
      render(
        <Card>
          <CardContent>Padded content</CardContent>
        </Card>
      )
      const content = screen.getByText('Padded content')
      expect(content).toHaveClass('px-6')
    })
  })

  describe('CardFooter', () => {
    it('renders card footer', () => {
      render(
        <Card>
          <CardFooter>Footer content</CardFooter>
        </Card>
      )
      const footer = screen.getByText('Footer content')
      expect(footer).toBeInTheDocument()
      expect(footer).toHaveAttribute('data-slot', 'card-footer')
    })

    it('has flex layout', () => {
      render(
        <Card>
          <CardFooter>Flex footer</CardFooter>
        </Card>
      )
      const footer = screen.getByText('Flex footer')
      expect(footer).toHaveClass('flex')
      expect(footer).toHaveClass('items-center')
    })
  })

  describe('CardAction', () => {
    it('renders card action', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
            <CardAction>Action button</CardAction>
          </CardHeader>
        </Card>
      )
      const action = screen.getByText('Action button')
      expect(action).toBeInTheDocument()
      expect(action).toHaveAttribute('data-slot', 'card-action')
    })

    it('positions action in grid', () => {
      render(
        <Card>
          <CardHeader>
            <CardAction>Positioned action</CardAction>
          </CardHeader>
        </Card>
      )
      const action = screen.getByText('Positioned action')
      expect(action).toHaveClass('col-start-2')
      expect(action).toHaveClass('row-span-2')
    })
  })

  describe('Complete Card composition', () => {
    it('renders full card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Project Status</CardTitle>
            <CardDescription>Current sprint overview</CardDescription>
            <CardAction>
              <button>Edit</button>
            </CardAction>
          </CardHeader>
          <CardContent>
            <p>Sprint progress: 75%</p>
          </CardContent>
          <CardFooter>
            <button>View Details</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByText('Project Status')).toBeInTheDocument()
      expect(screen.getByText('Current sprint overview')).toBeInTheDocument()
      expect(screen.getByText('Sprint progress: 75%')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /view details/i })).toBeInTheDocument()
    })

    it('allows custom content in any section', () => {
      render(
        <Card className="task-card">
          <CardHeader className="task-header">
            <CardTitle className="task-title">Custom Task</CardTitle>
          </CardHeader>
          <CardContent className="task-content">
            <div data-testid="custom-content">
              <span>Priority: High</span>
              <span>Status: In Progress</span>
            </div>
          </CardContent>
        </Card>
      )

      expect(screen.getByText('Custom Task')).toHaveClass('task-title')
      expect(screen.getByTestId('custom-content')).toBeInTheDocument()
      expect(screen.getByText('Priority: High')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('renders as semantic div elements', () => {
      render(
        <Card role="article">
          <CardHeader>
            <CardTitle>Accessible Card</CardTitle>
          </CardHeader>
        </Card>
      )
      expect(screen.getByRole('article')).toBeInTheDocument()
    })

    it('supports aria attributes', () => {
      render(
        <Card aria-labelledby="card-title">
          <CardHeader>
            <CardTitle id="card-title">Labeled Card</CardTitle>
          </CardHeader>
        </Card>
      )
      const card = screen.getByText('Labeled Card').closest('[data-slot="card"]')
      expect(card).toHaveAttribute('aria-labelledby', 'card-title')
    })
  })
})
