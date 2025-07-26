# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package called `seleniumlibraries` that provides utilities to reduce boilerplate code when working with Selenium WebDriver. The package includes:

- **Browser**: A wrapper around Chrome WebDriver with pre-configured options for headless operation, PDF handling, and download management
- **Element utilities**: Functions for reliable text extraction from web elements
- **WebPage**: A base class for page object pattern implementation

## Core Architecture

The package follows a modular structure:

- `seleniumlibraries/browser.py`: Contains the main `Browser` class with Chrome WebDriver setup, download waiting, PDF generation, and utility methods
- `seleniumlibraries/element.py`: Provides `get_text()` function for robust text extraction from WebElements
- `seleniumlibraries/page.py`: Contains `WebPage` base class for page object pattern
- `seleniumlibraries/__init__.py`: Package entry point that exports all public APIs

Key design patterns:
- Context manager support in `Browser` class for automatic cleanup
- Defensive programming in text extraction with fallbacks to `innerText` and `textContent`
- Hardcoded download directory at `/workspace/downloads`
- Chrome-specific optimizations for headless operation

## Development Commands

### Testing
```bash
# Run fast tests (default)
sudo -u selenium uv run invoke test

# Run all tests including slow ones  
sudo -u selenium uv run invoke test.all

# Run tests with coverage report
sudo -u selenium uv run invoke test.coverage
```

### Linting and Code Quality
```bash
# Fast linting (recommended for development)
invoke lint

# Deep linting (slower, more thorough)
invoke lint.deep

# Specific linters
invoke lint.ruff
invoke lint.flake8
invoke lint.mypy
invoke lint.pylint
invoke lint.bandit
```

### Code Formatting
```bash
# Format code
invoke style
```

### Building
```bash
# Build package
invoke dist

# Clean build artifacts
invoke clean
```

### Code Quality Tools Configuration

The project uses extensive linting and formatting tools configured in `pyproject.toml`:
- **Ruff**: Primary linter with comprehensive rule selection
- **Black**: Code formatting (line length: 119)
- **mypy**: Type checking with strict mode
- **flake8**: Additional linting with bugbear plugin
- **Pylint**: Comprehensive code analysis
- **bandit**: Security linting

## Browser Configuration

The `Browser` class is pre-configured with:
- Headless Chrome operation
- Custom user agent for compatibility
- Download directory: `/workspace/downloads`
- PDF printing capabilities via CDP
- Window size: 480x600
- 10-second default wait timeout

Root user execution is blocked for security reasons.