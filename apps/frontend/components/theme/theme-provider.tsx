import { createContext, useContext, useEffect, useState } from 'react'
import { useKV } from '@github/spark/hooks'

type Theme = 'light' | 'dark'
type PresetTheme = 'default' | 'github' | 'monokai' | 'solarized-light' | 'solarized-dark' | 
  'dracula' | 'nord' | 'gruvbox-light' | 'gruvbox-dark' | 'one-dark' | 'material' | 
  'tokyo-night' | 'catppuccin-latte' | 'catppuccin-mocha' | 'zenburn' | 'tomorrow' | 
  'tomorrow-night' | 'ayu-light' | 'ayu-dark' | 'palenight' | 'light-owl' | 'night-owl' | 
  'cobalt' | 'espresso' | 'synthwave' | 'forest' | 'ocean' | 'sunset' | 'monochrome'

interface ThemeContextType {
  theme: Theme
  presetTheme: PresetTheme
  setTheme: (theme: Theme) => void
  setPresetTheme: (presetTheme: PresetTheme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useKV<Theme>('app-theme', 'light')
  const [presetTheme, setPresetThemeState] = useKV<PresetTheme>('app-preset-theme', 'default')

  useEffect(() => {
    const root = document.documentElement
    
    // Remove all existing theme classes
    root.className = root.className
      .split(' ')
      .filter(cls => !cls.startsWith('theme-') && !cls.includes('-theme'))
      .join(' ')

    // Add current theme classes
    if (theme === 'dark') {
      root.classList.add('dark')
      root.classList.add('dark-theme')
    }
    
    // Add preset theme class
    if (presetTheme !== 'default') {
      root.classList.add(`theme-${presetTheme}`)
    }
  }, [theme, presetTheme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(() => newTheme)
  }

  const setPresetTheme = (newPresetTheme: PresetTheme) => {
    setPresetThemeState(() => newPresetTheme)
  }

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{
      theme: theme || 'light',
      presetTheme: presetTheme || 'default',
      setTheme,
      setPresetTheme,
      toggleTheme
    }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}