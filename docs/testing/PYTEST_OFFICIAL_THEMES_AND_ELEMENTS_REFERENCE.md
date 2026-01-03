# Pytest Official Themes and Elements Reference

> **Source**: Extracted from official Pytest and Rich library documentation via Context7
> **Date**: 2025-01-27
> **Authority**: Official documentation from pytest-dev/pytest and textualize/rich

## Overview

This document provides the authoritative list of pytest test output formatting and theming options based on official documentation.
Pytest uses the Rich library for enhanced terminal output formatting, and this reference covers all available elements, styles, and formatting options.## 1. Pytest Built-in Output Formatting Options

### 1.1 Verbosity Levels
- **`-q` / `--quiet`**: Quieter reporting (less verbose output)
- **`-qq`**: Even quieter output (minimal reporting)
- **`-v` / `--verbose`**: Verbose mode showing individual test details
- **`-vv`**: Extra verbose mode with detailed output

### 1.2 Traceback Styles (`--tb` option)
- **`--tb=auto`**: Default automatic traceback formatting
- **`--tb=long`**: Full traceback information
- **`--tb=short`**: Shortened traceback format
- **`--tb=no`**: No traceback output
- **`--tb=line`**: One line per failure

### 1.3 Test Result Reporting (`-r` option)
- **`-rf`**: Show info on failed tests
- **`-rs`**: Show info on skipped tests
- **`-rx`**: Show info on xfailed tests
- **`-rX`**: Show info on xpassed tests
- **`-ra`**: Show all except passed tests
- **`-rA`**: Show all test outcomes
- **`-rN`**: Disable all outcome reporting

### 1.4 Collection Display
- **`--collectonly`**: Show collected tests without running
- **`-q --collectonly`**: Quiet collection display
- **`-qq --collectonly`**: Minimal collection display

### 1.5 Doctest Reporting Styles
- **`--doctest-report=none`**: No doctest reporting
- **`--doctest-report=udiff`**: Unified diff format
- **`--doctest-report=cdiff`**: Context diff format
- **`--doctest-report=ndiff`**: ndiff format
- **`--doctest-report=only_first_failure`**: Show only first failure

## 2. Rich Library Styling Elements (Used by pytest)

### 2.1 Color Systems
- **`None`**: Disables color output
- **`auto`**: Automatically detects terminal color system
- **`standard`**: 16 colors (8 basic + bright variations)
- **`256`**: Standard 16 + 240 color palette
- **`truecolor`**: 16.7 million colors (24-bit)
- **`windows`**: 8 colors for legacy Windows terminals

### 2.2 Basic Style Attributes
- **`bold`**: Bold text weight
- **`dim`**: Dimmed/faded text
- **`italic`**: Italic text style
- **`underline`**: Underlined text
- **`strikethrough`**: Strikethrough text
- **`reverse`**: Reverse/inverse colors
- **`conceal`**: Hidden/concealed text
- **`frame`**: Framed text
- **`encircle`**: Encircled text

### 2.3 Standard Colors
- **`black`**: Black color
- **`red`**: Red color
- **`green`**: Green color
- **`yellow`**: Yellow color
- **`blue`**: Blue color
- **`magenta`**: Magenta color
- **`cyan`**: Cyan color
- **`white`**: White color
- **`default`**: Terminal default color

### 2.4 Bright Colors
- **`bright_black`**: Bright black (gray)
- **`bright_red`**: Bright red
- **`bright_green`**: Bright green
- **`bright_yellow`**: Bright yellow
- **`bright_blue`**: Bright blue
- **`bright_magenta`**: Bright magenta
- **`bright_cyan`**: Bright cyan
- **`bright_white`**: Bright white

### 2.5 Extended Color Names (256-color palette)
Selected examples from the Rich color palette:
- **`royal_blue1`**: #5f5fff (rgb(95,95,255))
- **`chartreuse4`**: #5f8700 (rgb(95,135,0))
- **`pale_turquoise4`**: #5f8787 (rgb(95,135,135))
- **`steel_blue`**: #5f87af (rgb(95,135,175))
- **`cornflower_blue`**: #5f87ff (rgb(95,135,255))
- **`dark_sea_green4`**: #5faf5f (rgb(95,175,95))
- **`cadet_blue`**: #5fafaf (rgb(95,175,175))
- **`sky_blue3`**: #5fafd7 (rgb(95,175,215))
- **`sea_green3`**: #5fd787 (rgb(95,215,135))
- **`medium_turquoise`**: #5fd7d7 (rgb(95,215,215))
- **`steel_blue1`**: #5fd7ff (rgb(95,215,255))
- **`dark_red`**: #870000 (rgb(135,0,0))

## 3. Environment Variables for Controlling Output

### 3.1 Color Control
- **`TERM`**: Terminal type (affects color support)
- **`FORCE_COLOR`**: Force color output regardless of terminal
- **`NO_COLOR`**: Disable all color output
- **`TTY_COMPATIBLE`**: Assume terminal compatibility
- **`TTY_INTERACTIVE`**: Control interactive mode

### 3.2 Dimension Control
- **`COLUMNS`**: Set console width
- **`LINES`**: Set console height
- **`JUPYTER_COLUMNS`**: Jupyter-specific width
- **`JUPYTER_LINES`**: Jupyter-specific height

## 4. Pytest Terminal Reporter Elements

### 4.1 Session Information
- **Platform information**: OS, Python version, pytest version
- **Root directory**: Test discovery root
- **Cache directory**: Pytest cache location
- **Collection summary**: Number of tests collected

### 4.2 Test Progress Indicators
- **`.`**: Passed test
- **`F`**: Failed test
- **`E`**: Error in test setup/teardown
- **`s`**: Skipped test
- **`x`**: Expected failure (xfail)
- **`X`**: Unexpected pass of xfail test
- **`P`**: Passed with output (when using -s)

### 4.3 Section Headers
- **`test session starts`**: Session beginning
- **`FAILURES`**: Failed test details section
- **`ERRORS`**: Error details section
- **`short test summary info`**: Summary section
- **`warnings summary`**: Warnings section

### 4.4 Markup Elements (Rich markup syntax)
- **`[bold]text[/bold]`**: Bold text
- **`[italic]text[/italic]`**: Italic text
- **`[underline]text[/underline]`**: Underlined text
- **`[strikethrough]text[/strikethrough]`**: Strikethrough text
- **`[red]text[/red]`**: Red colored text
- **`[green]text[/green]`**: Green colored text
- **`[blue]text[/blue]`**: Blue colored text
- **`[yellow]text[/yellow]`**: Yellow colored text
- **`[magenta]text[/magenta]`**: Magenta colored text
- **`[cyan]text[/cyan]`**: Cyan colored text

## 5. Theme Components for Custom Styling

### 5.1 Predefined Themes
- **`MONOKAI`**: Monokai color scheme
- **Custom themes**: User-defined color schemes

### 5.2 Theme Style Categories
- **`info`**: Informational messages
- **`warning`**: Warning messages
- **`danger`**: Error/critical messages
- **`success`**: Success messages
- **`header`**: Section headers
- **`emphasis`**: Emphasized text

## 6. Advanced Formatting Elements

### 6.1 Console Output Control
- **Line wrapping**: Automatic text wrapping to terminal width
- **Style inheritance**: Nested style application
- **Background colors**: `on_color` syntax (e.g., `white on blue`)
- **Default colors**: Reset to terminal defaults

### 6.2 Report Customization
- **Custom sections**: User-defined report sections
- **Property recording**: Test metadata recording
- **Report headers**: Session header customization
- **Terminal summary**: Custom summary information

## 7. Usage Examples

### 7.1 Basic Styling
```python
# Apply style to entire line
console.print("Test result", style="bold green")

# Use markup for inline styling
console.print("Test [bold red]FAILED[/bold red] with error")
```

### 7.2 Custom Theme Application
```python
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})

console = Console(theme=custom_theme)
console.print("This is information", style="info")
```

## 8. Official Documentation Sources

- **Pytest Documentation**: pytest-dev/pytest repository
- **Rich Library Documentation**: textualize/rich repository
- **Color Reference**: Rich library color palette documentation
- **Style Reference**: Rich library style system documentation

## Notes

1. This reference is based on official pytest and Rich library documentation
2. Color support depends on terminal capabilities
3. Some features may require specific pytest versions
4. Environment variables can override default behavior
5. Custom themes allow for consistent styling across applications

---

*Generated from official documentation sources via Context7 MCP integration*
