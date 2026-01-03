/**
 * CF-130 Phase 1.2: Input Component Tests
 * Tests for Input component behavior, validation states, and accessibility.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@/test/utils/test-utils'
import { Input } from '../input'

describe('Input', () => {
  describe('Rendering', () => {
    it('renders input element', () => {
      render(<Input placeholder="Enter text" />)
      const input = screen.getByPlaceholderText('Enter text')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('data-slot', 'input')
    })

    it('renders with default type text', () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'text')
    })

    it('applies custom className', () => {
      render(<Input className="custom-input" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('custom-input')
    })

    it('forwards ref correctly', () => {
      const ref = vi.fn()
      render(<Input ref={ref} />)
      expect(ref).toHaveBeenCalled()
    })
  })

  describe('Input Types', () => {
    it('renders text input', () => {
      render(<Input type="text" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'text')
    })

    it('renders password input', () => {
      render(<Input type="password" data-testid="password-input" />)
      const input = screen.getByTestId('password-input')
      expect(input).toHaveAttribute('type', 'password')
    })

    it('renders email input', () => {
      render(<Input type="email" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'email')
    })

    it('renders number input', () => {
      render(<Input type="number" />)
      const input = screen.getByRole('spinbutton')
      expect(input).toHaveAttribute('type', 'number')
    })

    it('renders search input', () => {
      render(<Input type="search" />)
      const input = screen.getByRole('searchbox')
      expect(input).toHaveAttribute('type', 'search')
    })
  })

  describe('User Interactions', () => {
    it('handles text input', () => {
      render(<Input />)
      const input = screen.getByRole('textbox')

      fireEvent.change(input, { target: { value: 'Hello World' } })
      expect(input).toHaveValue('Hello World')
    })

    it('calls onChange handler', () => {
      const handleChange = vi.fn()
      render(<Input onChange={handleChange} />)
      const input = screen.getByRole('textbox')

      fireEvent.change(input, { target: { value: 'test' } })
      expect(handleChange).toHaveBeenCalledTimes(1)
    })

    it('calls onFocus handler', () => {
      const handleFocus = vi.fn()
      render(<Input onFocus={handleFocus} />)
      const input = screen.getByRole('textbox')

      fireEvent.focus(input)
      expect(handleFocus).toHaveBeenCalledTimes(1)
    })

    it('calls onBlur handler', () => {
      const handleBlur = vi.fn()
      render(<Input onBlur={handleBlur} />)
      const input = screen.getByRole('textbox')

      fireEvent.blur(input)
      expect(handleBlur).toHaveBeenCalledTimes(1)
    })

    it('handles keyboard events', () => {
      const handleKeyDown = vi.fn()
      render(<Input onKeyDown={handleKeyDown} />)
      const input = screen.getByRole('textbox')

      fireEvent.keyDown(input, { key: 'Enter' })
      expect(handleKeyDown).toHaveBeenCalledTimes(1)
    })
  })

  describe('States', () => {
    it('handles disabled state', () => {
      render(<Input disabled />)
      const input = screen.getByRole('textbox')
      expect(input).toBeDisabled()
    })

    it('handles readonly state', () => {
      render(<Input readOnly value="Read only" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('readonly')
    })

    it('handles required state', () => {
      render(<Input required />)
      const input = screen.getByRole('textbox')
      expect(input).toBeRequired()
    })

    it('applies disabled styling', () => {
      render(<Input disabled />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('disabled:opacity-50')
    })
  })

  describe('Validation', () => {
    it('supports minLength validation', () => {
      render(<Input minLength={3} />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('minLength', '3')
    })

    it('supports maxLength validation', () => {
      render(<Input maxLength={10} />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('maxLength', '10')
    })

    it('supports pattern validation', () => {
      render(<Input pattern="[A-Za-z]+" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('pattern', '[A-Za-z]+')
    })

    it('has aria-invalid styling', () => {
      render(<Input aria-invalid="true" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-invalid', 'true')
      expect(input).toHaveClass('aria-invalid:border-destructive')
    })
  })

  describe('Placeholder', () => {
    it('displays placeholder text', () => {
      render(<Input placeholder="Enter your name" />)
      expect(screen.getByPlaceholderText('Enter your name')).toBeInTheDocument()
    })

    it('has placeholder styling', () => {
      render(<Input placeholder="Placeholder" />)
      const input = screen.getByPlaceholderText('Placeholder')
      expect(input).toHaveClass('placeholder:text-muted-foreground')
    })
  })

  describe('Accessibility', () => {
    it('supports aria-label', () => {
      render(<Input aria-label="Username input" />)
      expect(screen.getByLabelText('Username input')).toBeInTheDocument()
    })

    it('supports aria-describedby', () => {
      render(
        <>
          <Input aria-describedby="help-text" />
          <span id="help-text">Enter at least 8 characters</span>
        </>
      )
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-describedby', 'help-text')
    })

    it('has focus-visible styles for keyboard navigation', () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('focus-visible:border-ring')
      expect(input).toHaveClass('focus-visible:ring-ring/50')
    })

    it('can be associated with label via id', () => {
      render(
        <>
          <label htmlFor="email-input">Email</label>
          <Input id="email-input" type="email" />
        </>
      )
      expect(screen.getByLabelText('Email')).toBeInTheDocument()
    })
  })

  describe('File Input', () => {
    it('renders file input type', () => {
      render(<Input type="file" data-testid="file-input" />)
      const input = screen.getByTestId('file-input')
      expect(input).toHaveAttribute('type', 'file')
    })

    it('has file input styling', () => {
      render(<Input type="file" data-testid="file-input" />)
      const input = screen.getByTestId('file-input')
      expect(input).toHaveClass('file:text-foreground')
    })
  })
})
