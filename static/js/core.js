/**
 * @fileoverview Core JavaScript module for ServiceDispatch
 * @module core
 * @version 1.0.0
 * @description Provides uniform header/footer injection and core utilities
 *              across all HTML pages in the application.
 *
 * Usage: Include this script in any HTML page to automatically inject
 *        consistent header and footer elements with proper styling.
 *
 *        <script src="/static/js/core.js"></script>
 */

'use strict';

// =============================================================================
// SERVICEDISPATCH CORE MODULE
// =============================================================================

const ServiceDispatch = (function () {
    // -------------------------------------------------------------------------
    // Configuration
    // -------------------------------------------------------------------------

    const CONFIG = Object.freeze({
        APP_NAME: 'ServiceDispatch',
        VERSION: '1.0.0',
        THEME_STORAGE_KEY: 'servicedispatch-theme',
        DEFAULT_THEME: 'dark',
        SUPPORTED_THEMES: ['dark', 'light'],
        TRANSITION_DURATION: 300,
    });

    // -------------------------------------------------------------------------
    // Design Tokens (CSS Custom Properties)
    // -------------------------------------------------------------------------

    const DESIGN_TOKENS = `
        :root {
            /* Color Palette - Primary */
            --sd-color-primary-900: #0d1b2a;
            --sd-color-primary-800: #1b263b;
            --sd-color-primary-700: #1a365d;
            --sd-color-primary-600: #2c5282;
            --sd-color-primary-500: #3182ce;
            --sd-color-primary-400: #4299e1;
            --sd-color-primary-300: #63b3ed;
            --sd-color-primary-200: #90cdf4;
            --sd-color-primary-100: #bee3f8;
            --sd-color-primary-50:  #ebf8ff;

            /* Color Palette - Neutral */
            --sd-color-neutral-900: #0d1117;
            --sd-color-neutral-800: #161b22;
            --sd-color-neutral-700: #21262d;
            --sd-color-neutral-600: #30363d;
            --sd-color-neutral-500: #484f58;
            --sd-color-neutral-400: #6e7681;
            --sd-color-neutral-300: #8b949e;
            --sd-color-neutral-200: #c9d1d9;
            --sd-color-neutral-100: #e6edf3;
            --sd-color-neutral-50:  #f0f6fc;

            /* Semantic Colors */
            --sd-color-success: #238636;
            --sd-color-success-light: #2ea043;
            --sd-color-warning: #d29922;
            --sd-color-warning-light: #e3b341;
            --sd-color-error: #da3633;
            --sd-color-error-light: #f85149;
            --sd-color-info: #58a6ff;

            /* Typography */
            --sd-font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                                   Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
                                   'Helvetica Neue', sans-serif;
            --sd-font-family-mono: 'Cascadia Code', 'Fira Code', Consolas, 'Liberation Mono',
                                   Menlo, Monaco, monospace;

            /* Font Sizes */
            --sd-font-size-xs:   0.75rem;
            --sd-font-size-sm:   0.875rem;
            --sd-font-size-base: 1rem;
            --sd-font-size-lg:   1.125rem;
            --sd-font-size-xl:   1.25rem;
            --sd-font-size-2xl:  1.5rem;
            --sd-font-size-3xl:  1.875rem;

            /* Font Weights */
            --sd-font-weight-normal: 400;
            --sd-font-weight-medium: 500;
            --sd-font-weight-semibold: 600;
            --sd-font-weight-bold: 700;

            /* Spacing */
            --sd-spacing-1:  0.25rem;
            --sd-spacing-2:  0.5rem;
            --sd-spacing-3:  0.75rem;
            --sd-spacing-4:  1rem;
            --sd-spacing-5:  1.25rem;
            --sd-spacing-6:  1.5rem;
            --sd-spacing-8:  2rem;
            --sd-spacing-10: 2.5rem;
            --sd-spacing-12: 3rem;

            /* Border Radius */
            --sd-radius-sm: 0.25rem;
            --sd-radius-md: 0.375rem;
            --sd-radius-lg: 0.5rem;
            --sd-radius-xl: 0.75rem;
            --sd-radius-full: 9999px;

            /* Shadows */
            --sd-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --sd-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --sd-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);

            /* Transitions */
            --sd-transition-fast: 150ms ease;
            --sd-transition-normal: 250ms ease;
            --sd-transition-slow: 350ms ease;

            /* Z-Index */
            --sd-z-header: 1000;
            --sd-z-dropdown: 1010;
            --sd-z-modal: 1050;
            --sd-z-tooltip: 1070;

            /* Layout */
            --sd-container-max-width: 1600px;
            --sd-header-height: 64px;
            --sd-footer-height: 56px;
        }

        /* Dark Theme (Default) */
        [data-theme="dark"], :root {
            --sd-bg-primary: var(--sd-color-neutral-900);
            --sd-bg-secondary: var(--sd-color-neutral-800);
            --sd-bg-tertiary: var(--sd-color-neutral-700);
            --sd-bg-elevated: var(--sd-color-neutral-600);
            --sd-bg-header: linear-gradient(135deg, var(--sd-color-primary-700) 0%, var(--sd-color-primary-600) 100%);
            --sd-bg-footer: var(--sd-color-neutral-800);

            --sd-text-primary: var(--sd-color-neutral-100);
            --sd-text-secondary: var(--sd-color-neutral-300);
            --sd-text-muted: var(--sd-color-neutral-400);
            --sd-text-inverse: var(--sd-color-neutral-900);
            --sd-text-header: #ffffff;

            --sd-border-primary: var(--sd-color-neutral-600);
            --sd-border-secondary: var(--sd-color-neutral-700);

            --sd-accent-primary: var(--sd-color-primary-500);
            --sd-accent-hover: var(--sd-color-primary-400);
        }

        /* Light Theme */
        [data-theme="light"] {
            --sd-bg-primary: #f8fafc;
            --sd-bg-secondary: #ffffff;
            --sd-bg-tertiary: var(--sd-color-neutral-100);
            --sd-bg-elevated: #ffffff;
            --sd-bg-header: linear-gradient(135deg, var(--sd-color-primary-700) 0%, var(--sd-color-primary-600) 100%);
            --sd-bg-footer: var(--sd-color-neutral-100);

            --sd-text-primary: var(--sd-color-neutral-900);
            --sd-text-secondary: var(--sd-color-neutral-700);
            --sd-text-muted: var(--sd-color-neutral-500);
            --sd-text-inverse: var(--sd-color-neutral-50);
            --sd-text-header: #ffffff;

            --sd-border-primary: var(--sd-color-neutral-200);
            --sd-border-secondary: var(--sd-color-neutral-100);

            --sd-accent-primary: var(--sd-color-primary-600);
            --sd-accent-hover: var(--sd-color-primary-700);
        }
    `;

    // -------------------------------------------------------------------------
    // Base Styles
    // -------------------------------------------------------------------------

    const BASE_STYLES = `
        /* Reset & Base */
        *, *::before, *::after {
            box-sizing: border-box;
        }

        html {
            font-size: 16px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: var(--sd-font-family-sans);
            font-size: var(--sd-font-size-base);
            line-height: 1.5;
            color: var(--sd-text-primary);
            background-color: var(--sd-bg-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            transition: background-color var(--sd-transition-normal),
                        color var(--sd-transition-normal);
        }

        /* Focus Styles */
        :focus-visible {
            outline: 2px solid var(--sd-accent-primary);
            outline-offset: 2px;
        }

        /* Skip Link */
        .sd-skip-link {
            position: absolute;
            top: -100%;
            left: 50%;
            transform: translateX(-50%);
            padding: var(--sd-spacing-2) var(--sd-spacing-4);
            background: var(--sd-accent-primary);
            color: var(--sd-text-inverse);
            text-decoration: none;
            border-radius: var(--sd-radius-md);
            z-index: calc(var(--sd-z-header) + 1);
            transition: top var(--sd-transition-fast);
        }

        .sd-skip-link:focus {
            top: var(--sd-spacing-2);
        }

        /* Header */
        .sd-header {
            position: sticky;
            top: 0;
            z-index: var(--sd-z-header);
            background: var(--sd-bg-header);
            height: var(--sd-header-height);
            box-shadow: var(--sd-shadow-md);
        }

        .sd-header__container {
            max-width: var(--sd-container-max-width);
            margin: 0 auto;
            padding: 0 var(--sd-spacing-6);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .sd-header__brand {
            display: flex;
            align-items: center;
            gap: var(--sd-spacing-3);
            text-decoration: none;
            color: var(--sd-text-header);
        }

        .sd-header__logo {
            width: 32px;
            height: 32px;
        }

        .sd-header__title {
            font-size: var(--sd-font-size-xl);
            font-weight: var(--sd-font-weight-bold);
            letter-spacing: -0.025em;
        }

        .sd-header__nav {
            display: flex;
            align-items: center;
            gap: var(--sd-spacing-1);
        }

        .sd-header__link {
            padding: var(--sd-spacing-2) var(--sd-spacing-4);
            color: var(--sd-text-header);
            text-decoration: none;
            font-size: var(--sd-font-size-sm);
            font-weight: var(--sd-font-weight-medium);
            border-radius: var(--sd-radius-md);
            transition: background-color var(--sd-transition-fast);
            opacity: 0.9;
        }

        .sd-header__link:hover,
        .sd-header__link--active {
            background-color: rgba(255, 255, 255, 0.15);
            opacity: 1;
        }

        .sd-header__actions {
            display: flex;
            align-items: center;
            gap: var(--sd-spacing-2);
        }

        /* Theme Toggle Button */
        .sd-theme-toggle {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            padding: 0;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: var(--sd-radius-md);
            color: var(--sd-text-header);
            cursor: pointer;
            transition: all var(--sd-transition-fast);
        }

        .sd-theme-toggle:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .sd-theme-toggle__icon {
            width: 20px;
            height: 20px;
        }

        /* Logout Button */
        .sd-logout-btn {
            display: flex;
            align-items: center;
            gap: var(--sd-spacing-2);
            padding: var(--sd-spacing-2) var(--sd-spacing-4);
            background: var(--sd-color-error);
            border: none;
            border-radius: var(--sd-radius-md);
            color: #ffffff;
            font-size: var(--sd-font-size-sm);
            font-weight: var(--sd-font-weight-medium);
            cursor: pointer;
            transition: background-color var(--sd-transition-fast);
        }

        .sd-logout-btn:hover {
            background: var(--sd-color-error-light);
        }

        /* Main Content */
        .sd-main {
            flex: 1;
            width: 100%;
            max-width: var(--sd-container-max-width);
            margin: 0 auto;
            padding: var(--sd-spacing-6);
        }

        /* Footer */
        .sd-footer {
            background: var(--sd-bg-footer);
            border-top: 1px solid var(--sd-border-primary);
            padding: var(--sd-spacing-4) 0;
            margin-top: auto;
        }

        .sd-footer__container {
            max-width: var(--sd-container-max-width);
            margin: 0 auto;
            padding: 0 var(--sd-spacing-6);
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: var(--sd-spacing-4);
        }

        .sd-footer__copyright {
            font-size: var(--sd-font-size-sm);
            color: var(--sd-text-muted);
        }

        .sd-footer__links {
            display: flex;
            gap: var(--sd-spacing-6);
        }

        .sd-footer__link {
            font-size: var(--sd-font-size-sm);
            color: var(--sd-text-secondary);
            text-decoration: none;
            transition: color var(--sd-transition-fast);
        }

        .sd-footer__link:hover {
            color: var(--sd-accent-primary);
        }

        .sd-footer__meta {
            font-size: var(--sd-font-size-xs);
            color: var(--sd-text-muted);
            display: flex;
            align-items: center;
            gap: var(--sd-spacing-2);
        }

        .sd-footer__version {
            padding: var(--sd-spacing-1) var(--sd-spacing-2);
            background: var(--sd-bg-tertiary);
            border-radius: var(--sd-radius-sm);
            font-family: var(--sd-font-family-mono);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sd-header__nav {
                display: none;
            }

            .sd-footer__container {
                flex-direction: column;
                text-align: center;
            }

            .sd-footer__links {
                flex-wrap: wrap;
                justify-content: center;
            }
        }

        /* Print Styles */
        @media print {
            .sd-header,
            .sd-footer {
                display: none;
            }

            body {
                background: white;
                color: black;
            }
        }
    `;

    // -------------------------------------------------------------------------
    // SVG Icons
    // -------------------------------------------------------------------------

    const ICONS = {
        logo: `<svg viewBox="0 0 32 32" fill="currentColor" class="sd-header__logo">
            <path d="M16 2C8.268 2 2 8.268 2 16s6.268 14 14 14 14-6.268 14-14S23.732 2 16 2zm0 4c5.523 0 10 4.477 10 10s-4.477 10-10 10S6 21.523 6 16 10.477 6 16 6zm0 3a7 7 0 100 14 7 7 0 000-14zm0 2a5 5 0 110 10 5 5 0 010-10z"/>
            <circle cx="16" cy="16" r="2"/>
        </svg>`,
        sun: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sd-theme-toggle__icon">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>`,
        moon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sd-theme-toggle__icon">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>`,
        logout: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16,17 21,12 16,7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>`,
    };

    // -------------------------------------------------------------------------
    // Navigation Configuration
    // -------------------------------------------------------------------------

    const NAV_ITEMS = [
        { label: 'Dashboard', href: '/dashboard', id: 'dashboard' },
        { label: 'Tickets', href: '/tickets', id: 'tickets' },
        { label: 'Map', href: '/map', id: 'map' },
        { label: 'Analytics', href: '/analytics', id: 'analytics' },
        { label: 'Diagnosis', href: '/diagnosis', id: 'diagnosis' },
        { label: 'Parts', href: '/parts', id: 'parts' },
    ];

    const FOOTER_LINKS = [
        { label: 'Documentation', href: '/docs/' },
        { label: 'API Reference', href: '/api/' },
        { label: 'Support', href: '/support/' },
        { label: 'Privacy', href: '/privacy/' },
    ];

    // -------------------------------------------------------------------------
    // State
    // -------------------------------------------------------------------------

    let currentTheme = CONFIG.DEFAULT_THEME;
    let isInitialized = false;

    // -------------------------------------------------------------------------
    // Utility Functions
    // -------------------------------------------------------------------------

    /**
     * Get current page identifier from URL
     * @returns {string} Page identifier
     */
    function getCurrentPage() {
        const path = window.location.pathname;
        const match = path.match(/\/(\w+)/);
        return match ? match[1] : 'dashboard';
    }

    /**
     * Inject styles into document head
     * @param {string} css - CSS string to inject
     * @param {string} id - Style element ID
     */
    function injectStyles(css, id) {
        if (document.getElementById(id)) {
            return;
        }

        const style = document.createElement('style');
        style.id = id;
        style.textContent = css;
        document.head.appendChild(style);
    }

    /**
     * Create element with attributes and content
     * @param {string} tag - HTML tag name
     * @param {Object} attrs - Element attributes
     * @param {string|Node|Array} content - Element content
     * @returns {HTMLElement}
     */
    function createElement(tag, attrs = {}, content = null) {
        const el = document.createElement(tag);

        Object.entries(attrs).forEach(([key, value]) => {
            if (key === 'className') {
                el.className = value;
            } else if (key === 'dataset') {
                Object.entries(value).forEach(([dataKey, dataValue]) => {
                    el.dataset[dataKey] = dataValue;
                });
            } else if (key.startsWith('on') && typeof value === 'function') {
                el.addEventListener(key.slice(2).toLowerCase(), value);
            } else {
                el.setAttribute(key, value);
            }
        });

        if (content !== null) {
            if (typeof content === 'string') {
                el.innerHTML = content;
            } else if (Array.isArray(content)) {
                content.forEach((child) => {
                    if (child) {
                        el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
                    }
                });
            } else {
                el.appendChild(content);
            }
        }

        return el;
    }

    // -------------------------------------------------------------------------
    // Theme Management
    // -------------------------------------------------------------------------

    /**
     * Get stored theme or detect system preference
     * @returns {string} Theme identifier
     */
    function getInitialTheme() {
        const stored = localStorage.getItem(CONFIG.THEME_STORAGE_KEY);
        if (stored && CONFIG.SUPPORTED_THEMES.includes(stored)) {
            return stored;
        }

        if (window.matchMedia?.('(prefers-color-scheme: light)').matches) {
            return 'light';
        }

        return CONFIG.DEFAULT_THEME;
    }

    /**
     * Apply theme to document
     * @param {string} theme - Theme identifier
     */
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        currentTheme = theme;
        updateThemeToggle();
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem(CONFIG.THEME_STORAGE_KEY, newTheme);
        applyTheme(newTheme);
    }

    /**
     * Update theme toggle button appearance
     */
    function updateThemeToggle() {
        const toggle = document.querySelector('.sd-theme-toggle');
        if (toggle) {
            toggle.innerHTML = currentTheme === 'dark' ? ICONS.sun : ICONS.moon;
            toggle.setAttribute('aria-label', `Switch to ${currentTheme === 'dark' ? 'light' : 'dark'} theme`);
            toggle.setAttribute('aria-pressed', currentTheme === 'dark' ? 'false' : 'true');
        }
    }

    // -------------------------------------------------------------------------
    // Authentication
    // -------------------------------------------------------------------------

    /**
     * Handle logout action
     */
    async function handleLogout() {
        if (!confirm('Are you sure you want to log out?')) {
            return;
        }

        try {
            const response = await fetch('/api/logout', {
                method: 'POST',
                credentials: 'same-origin',
            });

            if (response.ok) {
                window.location.href = '/';
            } else {
                console.error('Logout failed');
                alert('Logout failed. Please try again.');
            }
        } catch (error) {
            console.error('Logout error:', error);
            // Fallback: redirect to login page
            window.location.href = '/';
        }
    }

    // -------------------------------------------------------------------------
    // Header Component
    // -------------------------------------------------------------------------

    /**
     * Create header element
     * @returns {HTMLElement}
     */
    function createHeader() {
        const currentPage = getCurrentPage();

        const navLinks = NAV_ITEMS.map((item) => {
            const isActive = item.id === currentPage;
            return createElement(
                'a',
                {
                    href: item.href,
                    className: `sd-header__link${isActive ? ' sd-header__link--active' : ''}`,
                    'aria-current': isActive ? 'page' : null,
                },
                item.label
            );
        });

        const header = createElement(
            'header',
            { className: 'sd-header', role: 'banner' },
            createElement('div', { className: 'sd-header__container' }, [
                // Brand
                createElement('a', { href: '/dashboard', className: 'sd-header__brand' }, [
                    createElement('span', {}, ICONS.logo),
                    createElement('span', { className: 'sd-header__title' }, CONFIG.APP_NAME),
                ]),

                // Navigation
                createElement('nav', { className: 'sd-header__nav', role: 'navigation', 'aria-label': 'Main navigation' }, navLinks),

                // Actions
                createElement('div', { className: 'sd-header__actions' }, [
                    // Theme Toggle
                    createElement(
                        'button',
                        {
                            className: 'sd-theme-toggle',
                            type: 'button',
                            'aria-label': 'Toggle theme',
                            onClick: toggleTheme,
                        },
                        currentTheme === 'dark' ? ICONS.sun : ICONS.moon
                    ),

                    // Logout Button
                    createElement(
                        'button',
                        {
                            className: 'sd-logout-btn',
                            type: 'button',
                            onClick: handleLogout,
                        },
                        [createElement('span', {}, ICONS.logout), 'Logout']
                    ),
                ]),
            ])
        );

        return header;
    }

    // -------------------------------------------------------------------------
    // Footer Component
    // -------------------------------------------------------------------------

    /**
     * Create footer element
     * @returns {HTMLElement}
     */
    function createFooter() {
        const currentYear = new Date().getFullYear();

        const footerLinks = FOOTER_LINKS.map((item) =>
            createElement('a', { href: item.href, className: 'sd-footer__link' }, item.label)
        );

        const footer = createElement(
            'footer',
            { className: 'sd-footer', role: 'contentinfo' },
            createElement('div', { className: 'sd-footer__container' }, [
                // Copyright
                createElement('div', { className: 'sd-footer__copyright' }, `© ${currentYear} ${CONFIG.APP_NAME}. All rights reserved.`),

                // Links
                createElement('nav', { className: 'sd-footer__links', 'aria-label': 'Footer navigation' }, footerLinks),

                // Meta
                createElement('div', { className: 'sd-footer__meta' }, [
                    createElement('span', {}, 'Version'),
                    createElement('span', { className: 'sd-footer__version' }, `v${CONFIG.VERSION}`),
                ]),
            ])
        );

        return footer;
    }

    // -------------------------------------------------------------------------
    // Skip Link Component
    // -------------------------------------------------------------------------

    /**
     * Create skip link for accessibility
     * @returns {HTMLElement}
     */
    function createSkipLink() {
        return createElement('a', { href: '#main-content', className: 'sd-skip-link' }, 'Skip to main content');
    }

    // -------------------------------------------------------------------------
    // Initialization
    // -------------------------------------------------------------------------

    /**
     * Initialize ServiceDispatch core module
     * Injects styles, header, and footer into the page
     */
    function init() {
        if (isInitialized) {
            return;
        }

        // Inject design tokens and base styles
        injectStyles(DESIGN_TOKENS + BASE_STYLES, 'sd-core-styles');

        // Apply initial theme
        currentTheme = getInitialTheme();
        applyTheme(currentTheme);

        // Wait for DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', injectComponents);
        } else {
            injectComponents();
        }

        // Listen for system theme changes
        window.matchMedia?.('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(CONFIG.THEME_STORAGE_KEY)) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });

        isInitialized = true;
    }

    /**
     * Inject header and footer components into page
     */
    function injectComponents() {
        // Only inject if not already present
        if (document.querySelector('.sd-header')) {
            return;
        }

        // Check if we're on a page that should have header/footer
        const path = window.location.pathname;
        const excludedPaths = ['/', '/login'];

        if (excludedPaths.includes(path)) {
            return;
        }

        // Create components
        const skipLink = createSkipLink();
        const header = createHeader();
        const footer = createFooter();

        // Insert skip link and header at start of body
        document.body.insertBefore(header, document.body.firstChild);
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Insert footer at end of body
        document.body.appendChild(footer);

        // Wrap main content if not already wrapped
        const mainContent = document.querySelector('main, .container, #content');
        if (mainContent && !mainContent.classList.contains('sd-main')) {
            mainContent.classList.add('sd-main');
            mainContent.id = 'main-content';
        }
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    return {
        init,
        toggleTheme,
        getCurrentTheme: () => currentTheme,
        setTheme: (theme) => {
            if (CONFIG.SUPPORTED_THEMES.includes(theme)) {
                localStorage.setItem(CONFIG.THEME_STORAGE_KEY, theme);
                applyTheme(theme);
            }
        },
        CONFIG,
    };
})();

// Auto-initialize
ServiceDispatch.init();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ServiceDispatch;
}
