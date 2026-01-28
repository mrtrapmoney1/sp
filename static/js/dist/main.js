"use strict";
/**
 * Main TypeScript Module - ServiceDispatch
 * Core functionality shared across all pages
 */
// =============================================================================
// Theme Management
// =============================================================================
class ThemeManager {
    static init() {
        const savedTheme = this.getSavedTheme();
        this.applyTheme(savedTheme);
    }
    static toggle() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.saveTheme(newTheme);
    }
    static getCurrentTheme() {
        return document.documentElement.getAttribute('data-bs-theme') || this.DEFAULT_THEME;
    }
    static getSavedTheme() {
        return localStorage.getItem(this.STORAGE_KEY) || this.DEFAULT_THEME;
    }
    static saveTheme(theme) {
        localStorage.setItem(this.STORAGE_KEY, theme);
    }
    static applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        this.updateThemeIcon(theme);
    }
    static updateThemeIcon(theme) {
        const icon = document.querySelector('#theme-toggle i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }
    }
}
ThemeManager.STORAGE_KEY = 'theme';
ThemeManager.DEFAULT_THEME = 'light';
// =============================================================================
// API Helper Functions
// =============================================================================
class ApiClient {
    static async request(url, method = 'GET', data) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            return result;
        }
        catch (error) {
            console.error('API request error:', error);
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error occurred',
            };
        }
    }
    static async get(url) {
        return this.request(url, 'GET');
    }
    static async post(url, data) {
        return this.request(url, 'POST', data);
    }
    static async put(url, data) {
        return this.request(url, 'PUT', data);
    }
    static async delete(url) {
        return this.request(url, 'DELETE');
    }
}
// =============================================================================
// Toast Notifications
// =============================================================================
class ToastManager {
    static init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            document.body.appendChild(this.container);
        }
    }
    static show(options) {
        if (!this.container)
            this.init();
        const config = typeof options === 'string'
            ? { message: options, type: 'info', duration: 4000 }
            : Object.assign({ type: 'info', duration: 4000 }, options);
        const toastId = `toast-${++this.toastCount}`;
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${config.type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${this.escapeHtml(config.message)}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        this.container.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            const bsToast = new window.bootstrap.Toast(toastElement, {
                autohide: config.type !== 'danger',
                delay: config.duration,
            });
            bsToast.show();
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }
    static success(message) {
        this.show({ message, type: 'success' });
    }
    static error(message) {
        this.show({ message, type: 'danger', duration: 0 });
    }
    static warning(message) {
        this.show({ message, type: 'warning' });
    }
    static info(message) {
        this.show({ message, type: 'info' });
    }
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
ToastManager.container = null;
ToastManager.toastCount = 0;
// =============================================================================
// Loading Overlay
// =============================================================================
class LoadingManager {
    static init() {
        this.overlay = document.getElementById('loading-overlay');
    }
    static show() {
        var _a;
        if (!this.overlay)
            this.init();
        (_a = this.overlay) === null || _a === void 0 ? void 0 : _a.classList.remove('d-none');
    }
    static hide() {
        var _a;
        if (!this.overlay)
            this.init();
        (_a = this.overlay) === null || _a === void 0 ? void 0 : _a.classList.add('d-none');
    }
}
LoadingManager.overlay = null;
// =============================================================================
// Utility Functions
// =============================================================================
class DateUtils {
    static formatDate(dateString) {
        if (!dateString)
            return '-';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime()))
                return dateString.toString();
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
            });
        }
        catch (_a) {
            return dateString.toString();
        }
    }
    static formatDateTime(dateString) {
        if (!dateString)
            return '-';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime()))
                return dateString.toString();
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        }
        catch (_a) {
            return dateString.toString();
        }
    }
    static toISODate(date) {
        return date.toISOString().split('T')[0];
    }
    static addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }
}
class StringUtils {
    static formatPhone(phone) {
        if (!phone)
            return '-';
        const digits = phone.replace(/\D/g, '');
        if (digits.length === 10) {
            return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
        }
        return phone;
    }
    static escapeHtml(text) {
        if (!text)
            return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    static truncate(text, maxLength) {
        if (!text || text.length <= maxLength)
            return text;
        return text.substring(0, maxLength) + '...';
    }
}
// =============================================================================
// Global Functions (for inline onclick handlers)
// =============================================================================
function showToast(message, type = 'info') {
    ToastManager.show({ message, type });
}
function showLoading() {
    LoadingManager.show();
}
function hideLoading() {
    LoadingManager.hide();
}
function toggleTheme() {
    ThemeManager.toggle();
}
function formatDate(dateString) {
    return DateUtils.formatDate(dateString);
}
function formatDateTime(dateString) {
    return DateUtils.formatDateTime(dateString);
}
function formatPhone(phone) {
    return StringUtils.formatPhone(phone);
}
function escapeHtml(text) {
    return StringUtils.escapeHtml(text);
}
// =============================================================================
// Initialization
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    ToastManager.init();
    LoadingManager.init();
    console.log('ServiceDispatch initialized');
});
// =============================================================================
// Exports (for module usage)
// =============================================================================
if (typeof window !== 'undefined') {
    window.ServiceDispatch = {
        ThemeManager,
        ApiClient,
        ToastManager,
        LoadingManager,
        DateUtils,
        StringUtils,
    };
}
//# sourceMappingURL=main.js.map