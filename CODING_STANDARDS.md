# ServiceDispatch Coding Standards

**Version:** 1.0.0
**Effective Date:** January 2026
**Author:** Principal Development Lead
**Classification:** Internal Engineering Standard

---

## Table of Contents

1. [Overview](#1-overview)
2. [General Principles](#2-general-principles)
3. [Python Standards](#3-python-standards)
4. [HTML/Jinja2 Standards](#4-htmljinja2-standards)
5. [CSS Standards](#5-css-standards)
6. [JavaScript Standards](#6-javascript-standards)
7. [API Design Standards](#7-api-design-standards)
8. [Security Standards](#8-security-standards)
9. [Documentation Standards](#9-documentation-standards)
10. [Testing Standards](#10-testing-standards)
11. [Version Control Standards](#11-version-control-standards)
12. [Performance Standards](#12-performance-standards)

---

## 1. Overview

### 1.1 Purpose

This document establishes the coding standards and best practices for the ServiceDispatch application. Adherence to these standards ensures code consistency, maintainability, security, and performance across the entire codebase.

### 1.2 Scope

These standards apply to all code within the ServiceDispatch ecosystem including:

- Backend Python/Flask applications
- Frontend HTML/CSS/JavaScript
- API integrations (SOAP/REST)
- Database operations
- Configuration management
- Documentation

### 1.3 Compliance

All code contributions must comply with these standards. Code reviews shall verify compliance prior to merge approval.

---

## 2. General Principles

### 2.1 SOLID Principles

| Principle | Description |
|-----------|-------------|
| **S**ingle Responsibility | Each module/class/function should have one reason to change |
| **O**pen/Closed | Open for extension, closed for modification |
| **L**iskov Substitution | Subtypes must be substitutable for their base types |
| **I**nterface Segregation | Many specific interfaces over one general interface |
| **D**ependency Inversion | Depend on abstractions, not concretions |

### 2.2 DRY (Don't Repeat Yourself)

- Extract common functionality into reusable modules
- Use template inheritance for shared HTML structures
- Centralize configuration values
- Create utility functions for repeated operations

### 2.3 KISS (Keep It Simple)

- Prefer clarity over cleverness
- Write self-documenting code
- Avoid premature optimization
- Choose simple solutions that meet requirements

### 2.4 Code Organization

```
sp/
├── app.py                    # Application entry point
├── config/
│   ├── __init__.py
│   ├── settings.py           # Environment configuration
│   └── constants.py          # Application constants
├── routes/
│   ├── __init__.py
│   ├── auth.py               # Authentication routes
│   ├── api.py                # API endpoints
│   └── views.py              # Template rendering routes
├── services/
│   ├── __init__.py
│   ├── soap_client.py        # SOAP/XML operations
│   ├── database.py           # DBF operations
│   └── analytics.py          # Data processing
├── static/
│   ├── css/
│   │   ├── base.css          # Foundation styles
│   │   ├── components.css    # UI component styles
│   │   └── themes.css        # Theme definitions
│   ├── js/
│   │   ├── core.js           # Core utilities
│   │   ├── theme.js          # Theme management
│   │   └── api.js            # API client
│   └── img/
│       └── favicon.ico
├── templates/
│   ├── base/
│   │   ├── header.html
│   │   └── footer.html
│   ├── layouts/
│   │   └── main.html
│   └── pages/
│       ├── index.html
│       ├── tickets.html
│       └── [...]
├── tests/
│   ├── __init__.py
│   ├── test_routes.py
│   ├── test_services.py
│   └── conftest.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 3. Python Standards

### 3.1 Style Guide

Follow PEP 8 with the following specifications:

| Rule | Standard |
|------|----------|
| Line Length | Maximum 120 characters |
| Indentation | 4 spaces (no tabs) |
| Quotes | Double quotes for strings |
| Imports | Grouped: stdlib, third-party, local |
| Blank Lines | 2 between top-level, 1 between methods |

### 3.2 Naming Conventions

```python
# Module names: lowercase with underscores
soap_client.py
database_operations.py

# Class names: PascalCase
class ServiceDispatchClient:
    pass

class TicketProcessor:
    pass

# Function/method names: snake_case
def get_service_calls():
    pass

def process_ticket_data():
    pass

# Constants: UPPERCASE with underscores
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"

# Private members: leading underscore
def _internal_helper():
    pass

class MyClass:
    def __init__(self):
        self._private_attribute = None
```

### 3.3 Type Hints

All functions must include type hints:

```python
from typing import Optional, List, Dict, Union, Tuple
from datetime import datetime

def fetch_service_calls(
    user_id: str,
    password: str,
    account: str,
    *,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_results: int = 100
) -> List[Dict[str, Union[str, int, float]]]:
    """
    Fetch service calls from ServicePower API.

    Args:
        user_id: ServicePower user identifier
        password: User authentication password
        account: Servicer account number
        start_date: Filter calls after this date
        end_date: Filter calls before this date
        max_results: Maximum number of results to return

    Returns:
        List of service call dictionaries containing call details

    Raises:
        AuthenticationError: If credentials are invalid
        APIConnectionError: If unable to connect to API
    """
    pass
```

### 3.4 Exception Handling

```python
# Define custom exceptions
class ServiceDispatchError(Exception):
    """Base exception for ServiceDispatch application."""
    pass

class AuthenticationError(ServiceDispatchError):
    """Raised when authentication fails."""
    pass

class APIConnectionError(ServiceDispatchError):
    """Raised when API connection fails."""
    pass

# Proper exception handling
def connect_to_api(credentials: Dict[str, str]) -> APIClient:
    try:
        client = APIClient(credentials)
        client.authenticate()
        return client
    except ConnectionError as e:
        logger.error(f"Failed to connect to API: {e}")
        raise APIConnectionError(f"Connection failed: {e}") from e
    except AuthError as e:
        logger.warning(f"Authentication failed for user: {credentials.get('user_id')}")
        raise AuthenticationError("Invalid credentials") from e
    finally:
        # Cleanup operations
        pass
```

### 3.5 Logging Standards

```python
import logging
from logging.handlers import RotatingFileHandler

# Logger configuration
def configure_logging(app_name: str, log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Format: timestamp - level - module - message
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        f"logs/{app_name}.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Usage
logger = configure_logging("servicedispatch")

# Log levels
logger.debug("Detailed diagnostic information")
logger.info("Confirmation that things are working")
logger.warning("Indication of potential problem")
logger.error("Serious problem, function failed")
logger.critical("Program may not be able to continue")
```

### 3.6 Flask Route Standards

```python
from flask import Blueprint, request, jsonify, render_template
from functools import wraps

# Create blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Route with proper error handling
@api_bp.route("/calls", methods=["GET", "POST"])
@require_auth
def get_calls():
    """
    Retrieve service calls.

    GET: Retrieve all calls with optional filters
    POST: Create a new service call
    """
    try:
        if request.method == "GET":
            filters = request.args.to_dict()
            calls = service.get_calls(**filters)
            return jsonify({"data": calls, "count": len(calls)}), 200

        elif request.method == "POST":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body required"}), 400

            result = service.create_call(data)
            return jsonify({"data": result}), 201

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except ServiceDispatchError as e:
        logger.error(f"Service error: {e}")
        return jsonify({"error": "Internal service error"}), 500
```

---

## 4. HTML/Jinja2 Standards

### 4.1 Template Structure

```html
{# templates/layouts/base.html #}
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{% block meta_description %}ServiceDispatch System{% endblock %}">

    <title>{% block title %}ServiceDispatch{% endblock %}</title>

    {# Favicon #}
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">

    {# Stylesheets #}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/themes.css') }}">
    {% block styles %}{% endblock %}
</head>
<body>
    {# Header #}
    {% include 'base/header.html' %}

    {# Main Content #}
    <main id="main-content" class="container">
        {% block content %}{% endblock %}
    </main>

    {# Footer #}
    {% include 'base/footer.html' %}

    {# Scripts #}
    <script src="{{ url_for('static', filename='js/core.js') }}"></script>
    <script src="{{ url_for('static', filename='js/theme.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 4.2 Naming Conventions

```html
<!-- Element IDs: kebab-case, descriptive -->
<div id="ticket-list-container">
<form id="service-call-form">
<button id="submit-ticket-btn">

<!-- Classes: BEM methodology -->
<div class="card">
    <div class="card__header">
        <h2 class="card__title">Title</h2>
    </div>
    <div class="card__body">
        <p class="card__text card__text--muted">Content</p>
    </div>
    <div class="card__footer">
        <button class="card__button card__button--primary">Action</button>
    </div>
</div>

<!-- Data attributes for JavaScript hooks -->
<button data-action="delete" data-ticket-id="{{ ticket.id }}">Delete</button>
<div data-component="chart" data-chart-type="bar"></div>
```

### 4.3 Accessibility Standards

```html
<!-- Semantic HTML -->
<header role="banner">
<nav role="navigation" aria-label="Main navigation">
<main role="main">
<footer role="contentinfo">

<!-- ARIA labels -->
<button aria-label="Close dialog" aria-describedby="close-description">
    <span class="sr-only">Close</span>
    <svg aria-hidden="true">...</svg>
</button>

<!-- Form accessibility -->
<form>
    <div class="form-group">
        <label for="customer-name" id="customer-name-label">Customer Name</label>
        <input
            type="text"
            id="customer-name"
            name="customerName"
            aria-labelledby="customer-name-label"
            aria-describedby="customer-name-help"
            aria-required="true"
            required
        >
        <span id="customer-name-help" class="form-help">Enter full legal name</span>
    </div>
</form>

<!-- Skip links -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

### 4.4 Jinja2 Best Practices

```html
{# Use comments for documentation #}
{# This template renders the ticket detail view #}

{# Prefer filters over function calls #}
{{ ticket.created_date | strftime('%Y-%m-%d') }}
{{ ticket.description | truncate(100) }}
{{ ticket.customer_name | title }}

{# Safe output only when necessary and verified #}
{{ trusted_html_content | safe }}

{# Use macros for reusable components #}
{% macro render_status_badge(status) %}
<span class="badge badge--{{ status | lower }}">
    {{ status | title }}
</span>
{% endmacro %}

{# Call macro #}
{{ render_status_badge(ticket.status) }}

{# Conditional classes #}
<div class="ticket {{ 'ticket--urgent' if ticket.priority == 'high' else '' }}">

{# Loop with index #}
{% for call in service_calls %}
<tr class="{{ 'row--alternate' if loop.index is odd else '' }}">
    <td>{{ loop.index }}</td>
    <td>{{ call.id }}</td>
</tr>
{% else %}
<tr>
    <td colspan="2">No service calls found</td>
</tr>
{% endfor %}
```

---

## 5. CSS Standards

### 5.1 Architecture

Use a modular CSS architecture:

```css
/* ==========================================================================
   BASE STYLES
   ========================================================================== */

/**
 * CSS Custom Properties (Design Tokens)
 * Define all design tokens at :root level
 */
:root {
    /* Color Palette */
    --color-primary-900: #0d1b2a;
    --color-primary-800: #1b263b;
    --color-primary-700: #1a365d;
    --color-primary-600: #2c5282;
    --color-primary-500: #3182ce;
    --color-primary-400: #4299e1;
    --color-primary-300: #63b3ed;
    --color-primary-200: #90cdf4;
    --color-primary-100: #bee3f8;
    --color-primary-50:  #ebf8ff;

    /* Neutral Palette */
    --color-neutral-900: #0d1117;
    --color-neutral-800: #161b22;
    --color-neutral-700: #21262d;
    --color-neutral-600: #30363d;
    --color-neutral-500: #484f58;
    --color-neutral-400: #6e7681;
    --color-neutral-300: #8b949e;
    --color-neutral-200: #c9d1d9;
    --color-neutral-100: #e6edf3;
    --color-neutral-50:  #f0f6fc;

    /* Semantic Colors */
    --color-success: #238636;
    --color-warning: #d29922;
    --color-error: #da3633;
    --color-info: #58a6ff;

    /* Typography */
    --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                        Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
                        'Helvetica Neue', sans-serif;
    --font-family-mono: 'Cascadia Code', 'Fira Code', Consolas, 'Liberation Mono',
                        Menlo, Monaco, monospace;

    --font-size-xs:   0.75rem;   /* 12px */
    --font-size-sm:   0.875rem;  /* 14px */
    --font-size-base: 1rem;      /* 16px */
    --font-size-lg:   1.125rem;  /* 18px */
    --font-size-xl:   1.25rem;   /* 20px */
    --font-size-2xl:  1.5rem;    /* 24px */
    --font-size-3xl:  1.875rem;  /* 30px */
    --font-size-4xl:  2.25rem;   /* 36px */

    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;

    --line-height-tight: 1.25;
    --line-height-normal: 1.5;
    --line-height-relaxed: 1.75;

    /* Spacing Scale */
    --spacing-0:  0;
    --spacing-1:  0.25rem;  /* 4px */
    --spacing-2:  0.5rem;   /* 8px */
    --spacing-3:  0.75rem;  /* 12px */
    --spacing-4:  1rem;     /* 16px */
    --spacing-5:  1.25rem;  /* 20px */
    --spacing-6:  1.5rem;   /* 24px */
    --spacing-8:  2rem;     /* 32px */
    --spacing-10: 2.5rem;   /* 40px */
    --spacing-12: 3rem;     /* 48px */
    --spacing-16: 4rem;     /* 64px */

    /* Border Radius */
    --radius-sm: 0.25rem;
    --radius-md: 0.375rem;
    --radius-lg: 0.5rem;
    --radius-xl: 0.75rem;
    --radius-2xl: 1rem;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1),
                 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1),
                 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1),
                 0 8px 10px -6px rgb(0 0 0 / 0.1);

    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
    --transition-slow: 350ms ease;

    /* Z-Index Scale */
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-popover: 1060;
    --z-tooltip: 1070;

    /* Layout */
    --container-max-width: 1600px;
    --sidebar-width: 280px;
    --header-height: 64px;
}
```

### 5.2 Theme System

```css
/* ==========================================================================
   THEME DEFINITIONS
   ========================================================================== */

/**
 * Dark Theme (Default)
 */
[data-theme="dark"] {
    --bg-primary: var(--color-neutral-900);
    --bg-secondary: var(--color-neutral-800);
    --bg-tertiary: var(--color-neutral-700);
    --bg-elevated: var(--color-neutral-600);

    --text-primary: var(--color-neutral-100);
    --text-secondary: var(--color-neutral-300);
    --text-muted: var(--color-neutral-400);
    --text-inverse: var(--color-neutral-900);

    --border-primary: var(--color-neutral-600);
    --border-secondary: var(--color-neutral-700);

    --accent-primary: var(--color-primary-500);
    --accent-hover: var(--color-primary-400);
}

/**
 * Light Theme
 */
[data-theme="light"] {
    --bg-primary: var(--color-neutral-50);
    --bg-secondary: #ffffff;
    --bg-tertiary: var(--color-neutral-100);
    --bg-elevated: #ffffff;

    --text-primary: var(--color-neutral-900);
    --text-secondary: var(--color-neutral-700);
    --text-muted: var(--color-neutral-500);
    --text-inverse: var(--color-neutral-50);

    --border-primary: var(--color-neutral-200);
    --border-secondary: var(--color-neutral-100);

    --accent-primary: var(--color-primary-600);
    --accent-hover: var(--color-primary-700);
}
```

### 5.3 Component Patterns

```css
/* ==========================================================================
   COMPONENT: Button
   ========================================================================== */

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-2);

    padding: var(--spacing-2) var(--spacing-4);

    font-family: var(--font-family-sans);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    line-height: var(--line-height-tight);
    text-decoration: none;

    border: 1px solid transparent;
    border-radius: var(--radius-md);

    cursor: pointer;
    transition: all var(--transition-fast);
}

.btn:focus-visible {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Button Variants */
.btn--primary {
    background-color: var(--accent-primary);
    color: var(--text-inverse);
}

.btn--primary:hover:not(:disabled) {
    background-color: var(--accent-hover);
}

.btn--secondary {
    background-color: transparent;
    border-color: var(--border-primary);
    color: var(--text-primary);
}

.btn--secondary:hover:not(:disabled) {
    background-color: var(--bg-tertiary);
}

.btn--danger {
    background-color: var(--color-error);
    color: var(--text-inverse);
}

/* Button Sizes */
.btn--sm {
    padding: var(--spacing-1) var(--spacing-3);
    font-size: var(--font-size-xs);
}

.btn--lg {
    padding: var(--spacing-3) var(--spacing-6);
    font-size: var(--font-size-base);
}
```

---

## 6. JavaScript Standards

### 6.1 Module Structure

```javascript
/**
 * @fileoverview Theme management module for ServiceDispatch
 * @module theme
 * @version 1.0.0
 */

'use strict';

/**
 * Theme configuration and management
 * @namespace Theme
 */
const Theme = (function() {
    // Private state
    const STORAGE_KEY = 'servicedispatch-theme';
    const THEMES = Object.freeze({
        DARK: 'dark',
        LIGHT: 'light'
    });

    let currentTheme = THEMES.DARK;

    /**
     * Initialize theme from storage or system preference
     * @private
     */
    function init() {
        const stored = localStorage.getItem(STORAGE_KEY);

        if (stored && Object.values(THEMES).includes(stored)) {
            currentTheme = stored;
        } else if (window.matchMedia?.('(prefers-color-scheme: light)').matches) {
            currentTheme = THEMES.LIGHT;
        }

        applyTheme(currentTheme);
        setupMediaQueryListener();
    }

    /**
     * Apply theme to document
     * @private
     * @param {string} theme - Theme identifier
     */
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        updateThemeToggle(theme);
    }

    /**
     * Update theme toggle button state
     * @private
     * @param {string} theme - Current theme
     */
    function updateThemeToggle(theme) {
        const toggle = document.querySelector('[data-action="toggle-theme"]');
        if (toggle) {
            toggle.setAttribute('aria-pressed', theme === THEMES.DARK);
            toggle.setAttribute('aria-label',
                `Switch to ${theme === THEMES.DARK ? 'light' : 'dark'} theme`
            );
        }
    }

    /**
     * Listen for system theme changes
     * @private
     */
    function setupMediaQueryListener() {
        window.matchMedia?.('(prefers-color-scheme: dark)')
            .addEventListener('change', (e) => {
                if (!localStorage.getItem(STORAGE_KEY)) {
                    setTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
                }
            });
    }

    // Public API
    return {
        /**
         * Get current theme
         * @returns {string} Current theme identifier
         */
        getCurrent() {
            return currentTheme;
        },

        /**
         * Set theme explicitly
         * @param {string} theme - Theme to apply
         */
        setTheme(theme) {
            if (!Object.values(THEMES).includes(theme)) {
                console.warn(`Invalid theme: ${theme}`);
                return;
            }

            currentTheme = theme;
            localStorage.setItem(STORAGE_KEY, theme);
            applyTheme(theme);
        },

        /**
         * Toggle between light and dark themes
         */
        toggle() {
            const newTheme = currentTheme === THEMES.DARK
                ? THEMES.LIGHT
                : THEMES.DARK;
            this.setTheme(newTheme);
        },

        /**
         * Available themes
         * @readonly
         */
        THEMES,

        /**
         * Initialize the theme system
         */
        init
    };
})();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => Theme.init());
```

### 6.2 Event Handling

```javascript
/**
 * @fileoverview Event delegation and handler management
 * @module events
 */

'use strict';

const EventManager = (function() {
    const handlers = new Map();

    /**
     * Register delegated event handler
     * @param {string} eventType - Event type (click, submit, etc.)
     * @param {string} selector - CSS selector for target elements
     * @param {Function} handler - Event handler function
     */
    function on(eventType, selector, handler) {
        if (!handlers.has(eventType)) {
            handlers.set(eventType, new Map());

            document.addEventListener(eventType, (event) => {
                const selectorMap = handlers.get(eventType);

                for (const [sel, fn] of selectorMap) {
                    const target = event.target.closest(sel);
                    if (target) {
                        fn.call(target, event, target);
                    }
                }
            }, true);
        }

        handlers.get(eventType).set(selector, handler);
    }

    /**
     * Remove event handler
     * @param {string} eventType - Event type
     * @param {string} selector - CSS selector
     */
    function off(eventType, selector) {
        handlers.get(eventType)?.delete(selector);
    }

    return { on, off };
})();

// Usage examples
EventManager.on('click', '[data-action="toggle-theme"]', (event) => {
    event.preventDefault();
    Theme.toggle();
});

EventManager.on('click', '[data-action="delete"]', async (event, target) => {
    const ticketId = target.dataset.ticketId;

    if (!confirm('Are you sure you want to delete this ticket?')) {
        return;
    }

    try {
        await API.deleteTicket(ticketId);
        target.closest('.ticket-row')?.remove();
    } catch (error) {
        console.error('Failed to delete ticket:', error);
        alert('Failed to delete ticket. Please try again.');
    }
});
```

### 6.3 API Client

```javascript
/**
 * @fileoverview API client for ServiceDispatch backend
 * @module api
 */

'use strict';

const API = (function() {
    const BASE_URL = '/api/v1';

    /**
     * Make HTTP request
     * @private
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     */
    async function request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new APIError(
                    error.message || response.statusText,
                    response.status,
                    error
                );
            }

            return response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError('Network error', 0, { originalError: error });
        }
    }

    /**
     * Custom API Error class
     */
    class APIError extends Error {
        constructor(message, status, data) {
            super(message);
            this.name = 'APIError';
            this.status = status;
            this.data = data;
        }
    }

    return {
        /**
         * Fetch service calls
         * @param {Object} filters - Optional filters
         * @returns {Promise<Array>} Service calls
         */
        async getCalls(filters = {}) {
            const params = new URLSearchParams(filters);
            return request(`/calls?${params}`);
        },

        /**
         * Create service call
         * @param {Object} data - Call data
         * @returns {Promise<Object>} Created call
         */
        async createCall(data) {
            return request('/calls', {
                method: 'POST',
                body: data
            });
        },

        /**
         * Delete ticket
         * @param {string} id - Ticket ID
         * @returns {Promise<void>}
         */
        async deleteTicket(id) {
            return request(`/tickets/${id}`, {
                method: 'DELETE'
            });
        },

        APIError
    };
})();
```

---

## 7. API Design Standards

### 7.1 RESTful Conventions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/calls` | List all calls |
| GET | `/api/v1/calls/{id}` | Get specific call |
| POST | `/api/v1/calls` | Create new call |
| PUT | `/api/v1/calls/{id}` | Update entire call |
| PATCH | `/api/v1/calls/{id}` | Partial update |
| DELETE | `/api/v1/calls/{id}` | Delete call |

### 7.2 Response Format

```json
{
    "success": true,
    "data": {
        "id": "TC-2026-001234",
        "customer": {
            "name": "John Smith",
            "phone": "402-555-0123"
        },
        "status": "scheduled",
        "created_at": "2026-01-22T10:30:00Z",
        "updated_at": "2026-01-22T14:45:00Z"
    },
    "meta": {
        "version": "1.0",
        "request_id": "req_abc123"
    }
}
```

### 7.3 Error Response Format

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request data",
        "details": [
            {
                "field": "customer.phone",
                "message": "Phone number format is invalid"
            }
        ]
    },
    "meta": {
        "version": "1.0",
        "request_id": "req_xyz789"
    }
}
```

### 7.4 HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET, PUT, PATCH, or DELETE |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no content) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate resource) |
| 422 | Unprocessable Entity (semantic error) |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## 8. Security Standards

### 8.1 Input Validation

```python
from typing import Any
import re

class Validator:
    """Input validation utilities."""

    PATTERNS = {
        'phone': re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'),
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'ticket_id': re.compile(r'^TC-\d{4}-\d{6}$'),
    }

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 255) -> str:
        """Remove potentially dangerous characters and limit length."""
        if not isinstance(value, str):
            raise ValueError("Expected string value")

        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')

        # Limit length
        return sanitized[:max_length].strip()

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number format."""
        return bool(cls.PATTERNS['phone'].match(phone))

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        return bool(cls.PATTERNS['email'].match(email))
```

### 8.2 Authentication

```python
from functools import wraps
from flask import session, redirect, url_for, request
import secrets
import hashlib

def generate_session_token() -> str:
    """Generate cryptographically secure session token."""
    return secrets.token_urlsafe(32)

def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """Hash password with salt using PBKDF2."""
    if salt is None:
        salt = secrets.token_bytes(32)

    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=100_000
    )

    return hashed.hex(), salt

def require_authentication(f):
    """Decorator to require authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            if request.is_json:
                return {'error': 'Authentication required'}, 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(role: str):
    """Decorator to require specific user role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('user_role')
            if user_role != role:
                return {'error': 'Insufficient permissions'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 8.3 CSRF Protection

```python
from flask import session, request, abort
from functools import wraps
import secrets

def generate_csrf_token() -> str:
    """Generate CSRF token and store in session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def validate_csrf(f):
    """Decorator to validate CSRF token on POST requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            token = request.headers.get('X-CSRF-Token') or \
                    request.form.get('csrf_token')

            if not token or token != session.get('csrf_token'):
                abort(403, description='Invalid CSRF token')

        return f(*args, **kwargs)
    return decorated_function
```

### 8.4 Environment Variables

```python
# config/settings.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    """Application settings from environment variables."""

    # Flask
    SECRET_KEY: str = os.environ.get('SECRET_KEY', '')
    DEBUG: bool = os.environ.get('DEBUG', 'false').lower() == 'true'

    # Database
    DATABASE_URL: str = os.environ.get('DATABASE_URL', '')

    # API Credentials (NEVER hardcode)
    API_USER_ID: str = os.environ.get('SERVICEPOWER_USER_ID', '')
    API_PASSWORD: str = os.environ.get('SERVICEPOWER_PASSWORD', '')
    API_ACCOUNT: str = os.environ.get('SERVICEPOWER_ACCOUNT', '')

    # API Endpoints
    API_BASE_URL: str = os.environ.get(
        'SERVICEPOWER_API_URL',
        'https://na-staging.servicepower.com'
    )

    def validate(self) -> None:
        """Validate required settings are present."""
        required = ['SECRET_KEY', 'API_USER_ID', 'API_PASSWORD']
        missing = [key for key in required if not getattr(self, key)]

        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

settings = Settings()
```

---

## 9. Documentation Standards

### 9.1 Code Comments

```python
def process_service_calls(
    calls: List[Dict[str, Any]],
    filter_status: Optional[str] = None
) -> ProcessingResult:
    """
    Process and aggregate service call data.

    This function performs the following operations:
    1. Filters calls by status (if specified)
    2. Groups calls by technician
    3. Calculates completion rates
    4. Generates summary statistics

    Args:
        calls: List of service call dictionaries from API
        filter_status: Optional status to filter by (e.g., 'completed', 'pending')

    Returns:
        ProcessingResult containing:
            - filtered_calls: List of calls matching criteria
            - by_technician: Dict mapping technician ID to their calls
            - statistics: Summary statistics dict

    Raises:
        ValueError: If calls list is empty
        KeyError: If required fields are missing from call data

    Example:
        >>> calls = api.get_calls()
        >>> result = process_service_calls(calls, filter_status='completed')
        >>> print(f"Completion rate: {result.statistics['completion_rate']:.1%}")

    Note:
        Performance: O(n) where n is the number of calls.
        For large datasets (>10,000 calls), consider using chunked processing.
    """
    pass
```

### 9.2 README Structure

```markdown
# Project Name

Brief description of the project.

## Prerequisites

- Python 3.11+
- Node.js 20+ (optional, for frontend tooling)
- Required API credentials

## Installation

\`\`\`bash
# Clone repository
git clone https://github.com/org/project.git
cd project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
\`\`\`

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Flask session secret | Yes |
| API_USER_ID | ServicePower user ID | Yes |
| API_PASSWORD | ServicePower password | Yes |

## Usage

\`\`\`bash
# Development
flask run --debug

# Production
gunicorn -w 4 -b 0.0.0.0:8000 app:app
\`\`\`

## API Documentation

See [API.md](docs/API.md) for detailed API documentation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

Proprietary - All rights reserved.
```

---

## 10. Testing Standards

### 10.1 Test Structure

```python
# tests/conftest.py
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    with client.session_transaction() as sess:
        sess['authenticated'] = True
        sess['user_id'] = 'test_user'
    return client
```

### 10.2 Test Naming

```python
# tests/test_api.py
import pytest

class TestServiceCallsAPI:
    """Tests for /api/v1/calls endpoint."""

    def test_get_calls_returns_list(self, authenticated_client):
        """GET /calls should return a list of service calls."""
        response = authenticated_client.get('/api/v1/calls')

        assert response.status_code == 200
        assert isinstance(response.json['data'], list)

    def test_get_calls_requires_authentication(self, client):
        """GET /calls should return 401 when not authenticated."""
        response = client.get('/api/v1/calls')

        assert response.status_code == 401

    def test_create_call_with_valid_data(self, authenticated_client):
        """POST /calls should create call with valid data."""
        data = {
            'customer_name': 'John Smith',
            'phone': '402-555-0123',
            'issue': 'Refrigerator not cooling'
        }

        response = authenticated_client.post('/api/v1/calls', json=data)

        assert response.status_code == 201
        assert response.json['data']['customer_name'] == 'John Smith'

    def test_create_call_validates_phone_format(self, authenticated_client):
        """POST /calls should reject invalid phone format."""
        data = {
            'customer_name': 'John Smith',
            'phone': 'invalid',
            'issue': 'Refrigerator not cooling'
        }

        response = authenticated_client.post('/api/v1/calls', json=data)

        assert response.status_code == 400
        assert 'phone' in response.json['error']['details'][0]['field']
```

### 10.3 Coverage Requirements

| Component | Minimum Coverage |
|-----------|-----------------|
| API Routes | 90% |
| Services | 85% |
| Utilities | 95% |
| Overall | 80% |

---

## 11. Version Control Standards

### 11.1 Branch Naming

```
main                    # Production-ready code
develop                 # Integration branch
feature/SD-123-add-map  # Feature branches
bugfix/SD-456-fix-auth  # Bug fix branches
hotfix/SD-789-critical  # Production hotfixes
release/v1.2.0          # Release branches
```

### 11.2 Commit Messages

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructure
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(tickets): add bulk export functionality

Implement DBF export for multiple tickets at once.
Users can now select multiple tickets and export
them to a single DBF file.

Closes #123
```

```
fix(auth): resolve session timeout issue

Session was expiring prematurely due to incorrect
timezone handling in token validation.

Fixes #456
```

### 11.3 Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

---

## 12. Performance Standards

### 12.1 Response Time Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| Page Load | < 1s | 3s |
| API Response | < 200ms | 1s |
| Database Query | < 50ms | 200ms |
| File Operation | < 100ms | 500ms |

### 12.2 Optimization Guidelines

```python
# Use generator expressions for large datasets
def process_large_dataset(records):
    # Good: Generator expression
    return (process(r) for r in records)

    # Bad: List comprehension for large data
    # return [process(r) for r in records]

# Use caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def get_product_info(product_id: str) -> dict:
    """Fetch and cache product information."""
    return api.fetch_product(product_id)

# Batch database operations
def bulk_insert_records(records: List[dict]) -> None:
    """Insert records in batches for performance."""
    BATCH_SIZE = 1000

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        db.insert_many(batch)
```

### 12.3 Frontend Performance

```javascript
// Debounce user input
function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Use for search input
const handleSearch = debounce((query) => {
    API.search(query).then(updateResults);
}, 300);

// Lazy load images
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            observer.unobserve(img);
        }
    });
});

document.querySelectorAll('img[data-src]').forEach(img => {
    observer.observe(img);
});
```

---

## Appendix A: Quick Reference

### File Extensions

| Type | Extension |
|------|-----------|
| Python | `.py` |
| HTML Templates | `.html` |
| CSS | `.css` |
| JavaScript | `.js` |
| Markdown | `.md` |
| Configuration | `.yml`, `.json` |
| Environment | `.env` |

### Import Order

```python
# 1. Standard library
import os
import sys
from datetime import datetime
from typing import Optional, List

# 2. Third-party packages
import flask
from flask import Blueprint, request
import pandas as pd

# 3. Local application
from config import settings
from services.soap_client import SOAPClient
from utils.validators import Validator
```

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-22 | Principal Development Lead | Initial release |

---

*This document is the authoritative source for coding standards within the ServiceDispatch project. All team members are expected to familiarize themselves with and adhere to these standards.*
