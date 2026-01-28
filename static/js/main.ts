/**
 * Main TypeScript Module - ServiceDispatch
 * Core functionality shared across all pages
 */

// =============================================================================
// Type Definitions
// =============================================================================

interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
    meta?: {
        count?: number;
        page?: number;
        total_pages?: number;
    };
}

interface ToastOptions {
    message: string;
    type?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark';
    duration?: number;
}

// =============================================================================
// Theme Management
// =============================================================================

class ThemeManager {
    private static readonly STORAGE_KEY = 'theme';
    private static readonly DEFAULT_THEME = 'light';

    static init(): void {
        const savedTheme = this.getSavedTheme();
        this.applyTheme(savedTheme);
    }

    static toggle(): void {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.saveTheme(newTheme);
    }

    private static getCurrentTheme(): string {
        return document.documentElement.getAttribute('data-bs-theme') || this.DEFAULT_THEME;
    }

    private static getSavedTheme(): string {
        return localStorage.getItem(this.STORAGE_KEY) || this.DEFAULT_THEME;
    }

    private static saveTheme(theme: string): void {
        localStorage.setItem(this.STORAGE_KEY, theme);
    }

    private static applyTheme(theme: string): void {
        document.documentElement.setAttribute('data-bs-theme', theme);
        this.updateThemeIcon(theme);
    }

    private static updateThemeIcon(theme: string): void {
        const icon = document.querySelector('#theme-toggle i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }
    }
}

// =============================================================================
// API Helper Functions
// =============================================================================

class ApiClient {
    static async request<T = any>(
        url: string,
        method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
        data?: any
    ): Promise<ApiResponse<T>> {
        const options: RequestInit = {
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
            const result: ApiResponse<T> = await response.json();
            return result;
        } catch (error) {
            console.error('API request error:', error);
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error occurred',
            };
        }
    }

    static async get<T = any>(url: string): Promise<ApiResponse<T>> {
        return this.request<T>(url, 'GET');
    }

    static async post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
        return this.request<T>(url, 'POST', data);
    }

    static async put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
        return this.request<T>(url, 'PUT', data);
    }

    static async delete<T = any>(url: string): Promise<ApiResponse<T>> {
        return this.request<T>(url, 'DELETE');
    }
}

// =============================================================================
// Toast Notifications
// =============================================================================

class ToastManager {
    private static container: HTMLElement | null = null;
    private static toastCount = 0;

    static init(): void {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            document.body.appendChild(this.container);
        }
    }

    static show(options: ToastOptions | string): void {
        if (!this.container) this.init();

        const config: ToastOptions = typeof options === 'string'
            ? { message: options, type: 'info', duration: 4000 }
            : { type: 'info', duration: 4000, ...options };

        const toastId = `toast-${++this.toastCount}`;
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${config.type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${this.escapeHtml(config.message)}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        this.container!.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            const bsToast = new (window as any).bootstrap.Toast(toastElement, {
                autohide: config.type !== 'danger',
                delay: config.duration,
            });
            bsToast.show();

            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }

    static success(message: string): void {
        this.show({ message, type: 'success' });
    }

    static error(message: string): void {
        this.show({ message, type: 'danger', duration: 0 });
    }

    static warning(message: string): void {
        this.show({ message, type: 'warning' });
    }

    static info(message: string): void {
        this.show({ message, type: 'info' });
    }

    private static escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// =============================================================================
// Loading Overlay
// =============================================================================

class LoadingManager {
    private static overlay: HTMLElement | null = null;

    static init(): void {
        this.overlay = document.getElementById('loading-overlay');
    }

    static show(): void {
        if (!this.overlay) this.init();
        this.overlay?.classList.remove('d-none');
    }

    static hide(): void {
        if (!this.overlay) this.init();
        this.overlay?.classList.add('d-none');
    }
}

// =============================================================================
// Utility Functions
// =============================================================================

class DateUtils {
    static formatDate(dateString: string | Date): string {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString.toString();
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
            });
        } catch {
            return dateString.toString();
        }
    }

    static formatDateTime(dateString: string | Date): string {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString.toString();
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        } catch {
            return dateString.toString();
        }
    }

    static toISODate(date: Date): string {
        return date.toISOString().split('T')[0];
    }

    static addDays(date: Date, days: number): Date {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }
}

class StringUtils {
    static formatPhone(phone: string): string {
        if (!phone) return '-';
        const digits = phone.replace(/\D/g, '');
        if (digits.length === 10) {
            return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
        }
        return phone;
    }

    static escapeHtml(text: string): string {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static truncate(text: string, maxLength: number): string {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// =============================================================================
// Global Functions (for inline onclick handlers)
// =============================================================================

function showToast(message: string, type: ToastOptions['type'] = 'info'): void {
    ToastManager.show({ message, type });
}

function showLoading(): void {
    LoadingManager.show();
}

function hideLoading(): void {
    LoadingManager.hide();
}

function toggleTheme(): void {
    ThemeManager.toggle();
}

function formatDate(dateString: string | Date): string {
    return DateUtils.formatDate(dateString);
}

function formatDateTime(dateString: string | Date): string {
    return DateUtils.formatDateTime(dateString);
}

function formatPhone(phone: string): string {
    return StringUtils.formatPhone(phone);
}

function escapeHtml(text: string): string {
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
    (window as any).ServiceDispatch = {
        ThemeManager,
        ApiClient,
        ToastManager,
        LoadingManager,
        DateUtils,
        StringUtils,
    };
}
