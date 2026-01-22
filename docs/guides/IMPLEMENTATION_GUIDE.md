# ServiceDispatch Implementation Guide

This guide explains how to use the new unified styling system, header/footer components, and configuration files.

---

## Quick Start

### 1. Update Existing Templates

Replace your current template headers with the new layout system:

**Before (old approach):**
```html
{% extends "header.html" %}
{% block content %}
...
{% endblock %}
```

**After (new approach):**
```html
{% extends "layouts/main.html" %}

{% block title %}Page Title{% endblock %}

{% block styles %}
<!-- Page-specific CSS here -->
{% endblock %}

{% block content %}
<div class="container">
    <!-- Your content here -->
</div>
{% endblock %}

{% block scripts %}
<!-- Page-specific JavaScript here -->
{% endblock %}
```

---

## File Structure

```
sp/
├── static/
│   ├── css/
│   │   ├── base.css          # Foundation styles, design tokens
│   │   ├── components.css    # UI components (buttons, forms, etc.)
│   │   └── themes.css        # Dark/light theme definitions
│   ├── js/
│   │   └── core.js           # Core utilities, theme toggle, header/footer
│   └── img/
│       └── favicon.svg       # Application favicon
├── templates/
│   ├── base/
│   │   ├── header.html       # Unified header component
│   │   └── footer.html       # Unified footer component
│   ├── layouts/
│   │   └── main.html         # Main page layout template
│   └── pages/                # Your page templates
├── _config.yml               # Jekyll configuration (for docs site)
├── Gemfile                   # Ruby dependencies (for Jekyll)
├── package.json              # Node.js dependencies
├── .env.example              # Environment variable template
├── CODING_STANDARDS.md       # Development standards
└── search_data.json          # Search index data
```

---

## Using the Design System

### CSS Custom Properties (Design Tokens)

All styling uses CSS custom properties for consistency. Reference them in your CSS:

```css
.my-component {
    /* Colors */
    background-color: var(--bg-elevated);
    color: var(--text-primary);
    border: 1px solid var(--border-primary);

    /* Typography */
    font-family: var(--font-sans);
    font-size: var(--text-base);
    font-weight: var(--weight-medium);

    /* Spacing */
    padding: var(--space-4);
    margin-bottom: var(--space-6);

    /* Borders */
    border-radius: var(--radius-lg);

    /* Shadows */
    box-shadow: var(--shadow-md);

    /* Transitions */
    transition: all var(--duration-200) var(--ease-out);
}
```

### Theme-Aware Styling

Components automatically adapt to the current theme. The theme is controlled via the `data-theme` attribute on `<html>`:

```html
<html data-theme="dark">  <!-- or "light" -->
```

Use theme-specific styling when needed:

```css
/* Default (works in both themes) */
.component {
    background: var(--bg-elevated);
}

/* Dark theme specific */
[data-theme="dark"] .component {
    border-color: var(--color-neutral-700);
}

/* Light theme specific */
[data-theme="light"] .component {
    border-color: var(--color-neutral-200);
}
```

---

## Component Library

### Buttons

```html
<!-- Primary Button -->
<button class="btn btn--primary">Primary Action</button>

<!-- Secondary Button -->
<button class="btn btn--secondary">Secondary</button>

<!-- Danger Button -->
<button class="btn btn--danger">Delete</button>

<!-- Sizes -->
<button class="btn btn--primary btn--sm">Small</button>
<button class="btn btn--primary btn--lg">Large</button>

<!-- Icon Button -->
<button class="btn btn--icon btn--secondary">
    <svg>...</svg>
</button>
```

### Forms

```html
<div class="form-group">
    <label for="name" class="form-label form-label--required">Name</label>
    <input type="text" id="name" class="form-input" placeholder="Enter name">
    <span class="form-help">Enter your full legal name</span>
</div>

<!-- Error State -->
<div class="form-group">
    <label for="email" class="form-label">Email</label>
    <input type="email" id="email" class="form-input form-input--error">
    <span class="form-error">Please enter a valid email address</span>
</div>
```

### Cards

```html
<div class="card">
    <div class="card__header">
        <h3 class="card__title">Card Title</h3>
    </div>
    <div class="card__body">
        <p>Card content goes here.</p>
    </div>
    <div class="card__footer">
        <button class="btn btn--primary">Action</button>
    </div>
</div>
```

### Badges

```html
<span class="badge badge--default">Default</span>
<span class="badge badge--primary">Primary</span>
<span class="badge badge--success">Success</span>
<span class="badge badge--warning">Warning</span>
<span class="badge badge--error">Error</span>
```

### Tables

```html
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>001</td>
                <td>John Smith</td>
                <td><span class="badge badge--success">Active</span></td>
            </tr>
        </tbody>
    </table>
</div>
```

### Stat Cards

```html
<div class="stat-card">
    <div class="stat-card__label">Total Tickets</div>
    <div class="stat-card__value">1,234</div>
    <div class="stat-card__change stat-card__change--positive">
        <svg>...</svg> +12%
    </div>
</div>
```

---

## Theme Toggle

The theme can be toggled programmatically:

```javascript
// Toggle between themes
ServiceDispatch.toggleTheme();

// Set specific theme
ServiceDispatch.setTheme('light');
ServiceDispatch.setTheme('dark');

// Get current theme
const theme = ServiceDispatch.getCurrentTheme();
```

---

## Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```
   SECRET_KEY=your-generated-secret-key
   SERVICEPOWER_USER_ID=your-user-id
   SERVICEPOWER_PASSWORD=your-password
   ```

3. Never commit `.env` to version control.

---

## Jekyll Documentation Site

To run the documentation site locally:

```bash
# Install Ruby dependencies
bundle install

# Start Jekyll server
bundle exec jekyll serve --livereload
```

The site will be available at `http://localhost:4000`.

---

## NPM Scripts

```bash
# Development (watch CSS and JS)
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Format code
npm run format

# Run tests
npm run test
```

---

## Migration Checklist

- [ ] Update templates to extend `layouts/main.html`
- [ ] Replace inline styles with CSS classes from `components.css`
- [ ] Use design tokens instead of hardcoded values
- [ ] Test dark and light themes
- [ ] Verify responsive behavior on mobile
- [ ] Run accessibility checks (keyboard navigation, screen readers)
- [ ] Update environment variables in `.env`

---

## Best Practices

1. **Always use design tokens** - Never hardcode colors, spacing, or typography values.

2. **Mobile-first responsive design** - Start with mobile styles, then add breakpoints for larger screens.

3. **Semantic HTML** - Use appropriate HTML elements (`<button>`, `<nav>`, `<main>`, etc.).

4. **Accessibility** - Include ARIA labels, maintain keyboard focus, ensure color contrast.

5. **Performance** - Minimize inline styles, defer non-critical JavaScript, optimize images.

---

## Support

For questions or issues with the design system:

1. Review the [Coding Standards](CODING_STANDARDS.md)
2. Check existing components in `static/css/components.css`
3. Consult the design tokens in `static/css/base.css`
