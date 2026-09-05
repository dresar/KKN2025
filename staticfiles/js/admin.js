// Admin JavaScript - Error Detection and Monitoring

// Global Error Monitoring
class ErrorMonitor {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.apiErrors = [];
        this.csrfErrors = [];
        this.init();
    }

    init() {
        this.setupGlobalErrorHandling();
        this.setupCSRFMonitoring();
        this.setupAPIMonitoring();
        this.setupFormValidation();
        this.setupConsoleLogging();
        console.log('🔍 Error Monitor initialized');
    }

    setupGlobalErrorHandling() {
        // Catch JavaScript errors
        window.addEventListener('error', (event) => {
            this.logError('JavaScript Error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            });
        });

        // Catch unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.logError('Unhandled Promise Rejection', {
                reason: event.reason,
                promise: event.promise
            });
        });
    }

    setupCSRFMonitoring() {
        // Monitor CSRF token presence
        const checkCSRF = () => {
            const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]');
            if (!csrfToken) {
                this.logWarning('CSRF Token Missing', 'No CSRF token found in form');
                return false;
            }
            
            if (!csrfToken.value || csrfToken.value.length < 10) {
                this.logError('CSRF Token Invalid', 'CSRF token appears to be invalid');
                return false;
            }
            
            return true;
        };

        // Check CSRF on page load
        document.addEventListener('DOMContentLoaded', checkCSRF);
        
        // Check CSRF before form submissions
        document.addEventListener('submit', (event) => {
            if (!checkCSRF()) {
                this.showNotification('CSRF token missing or invalid!', 'error');
            }
        });
    }

    setupAPIMonitoring() {
        // Override fetch to monitor API calls
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = Date.now();
            try {
                const response = await originalFetch(...args);
                const duration = Date.now() - startTime;
                
                if (!response.ok) {
                    this.logAPIError(args[0], response.status, response.statusText, duration);
                } else {
                    console.log(`✅ API Success: ${args[0]} (${duration}ms)`);
                }
                
                return response;
            } catch (error) {
                const duration = Date.now() - startTime;
                this.logAPIError(args[0], 'Network Error', error.message, duration);
                throw error;
            }
        };
    }

    setupFormValidation() {
        // Enhanced form validation
        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (form.tagName === 'FORM') {
                this.validateForm(form);
            }
        });

        // Real-time field validation
        document.addEventListener('blur', (event) => {
            if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT' || event.target.tagName === 'TEXTAREA') {
                this.validateField(event.target);
            }
        }, true);
    }

    setupConsoleLogging() {
        // Enhanced console logging
        const originalConsoleError = console.error;
        console.error = (...args) => {
            this.logError('Console Error', args.join(' '));
            originalConsoleError.apply(console, args);
        };

        const originalConsoleWarn = console.warn;
        console.warn = (...args) => {
            this.logWarning('Console Warning', args.join(' '));
            originalConsoleWarn.apply(console, args);
        };
    }

    validateForm(form) {
        let hasErrors = false;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.markFieldError(field, 'This field is required');
                hasErrors = true;
            } else {
                this.markFieldSuccess(field);
            }
        });

        // Validate specific field types
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                this.markFieldError(field, 'Please enter a valid email address');
                hasErrors = true;
            }
        });

        const nikFields = form.querySelectorAll('input[name="nik"]');
        nikFields.forEach(field => {
            if (field.value && !this.isValidNIK(field.value)) {
                this.markFieldError(field, 'NIK must be 16 digits');
                hasErrors = true;
            }
        });

        return !hasErrors;
    }

    validateField(field) {
        // Remove previous error styling
        field.classList.remove('field-error', 'field-success');
        const errorMsg = field.parentNode.querySelector('.error-message');
        if (errorMsg) errorMsg.remove();

        // Validate based on field type
        if (field.hasAttribute('required') && !field.value.trim()) {
            this.markFieldError(field, 'This field is required');
            return false;
        }

        if (field.type === 'email' && field.value && !this.isValidEmail(field.value)) {
            this.markFieldError(field, 'Please enter a valid email address');
            return false;
        }

        if (field.name === 'nik' && field.value && !this.isValidNIK(field.value)) {
            this.markFieldError(field, 'NIK must be 16 digits');
            return false;
        }

        this.markFieldSuccess(field);
        return true;
    }

    markFieldError(field, message) {
        field.classList.add('field-error');
        field.classList.remove('field-success');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    markFieldSuccess(field) {
        field.classList.add('field-success');
        field.classList.remove('field-error');
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidNIK(nik) {
        return /^\d{16}$/.test(nik);
    }

    logError(type, details) {
        const error = {
            type,
            details,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        this.errors.push(error);
        console.error(`❌ ${type}:`, details);
        
        // Show notification for critical errors
        if (type.includes('CSRF') || type.includes('API')) {
            this.showNotification(`${type}: ${JSON.stringify(details)}`, 'error');
        }
    }

    logWarning(type, details) {
        const warning = {
            type,
            details,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        this.warnings.push(warning);
        console.warn(`⚠️ ${type}:`, details);
    }

    logAPIError(url, status, message, duration) {
        const apiError = {
            url,
            status,
            message,
            duration,
            timestamp: new Date().toISOString()
        };
        
        this.apiErrors.push(apiError);
        console.error(`❌ API Error: ${url} - ${status} ${message} (${duration}ms)`);
        
        this.showNotification(`API Error: ${url} - ${status}`, 'error');
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existing = document.querySelectorAll('.notification');
        existing.forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    getErrorReport() {
        return {
            errors: this.errors,
            warnings: this.warnings,
            apiErrors: this.apiErrors,
            csrfErrors: this.csrfErrors,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };
    }

    downloadErrorReport() {
        const report = this.getErrorReport();
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `error-report-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Utility Functions
function getCsrfToken() {
    const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : null;
}

function showLoading(element) {
    if (element) {
        element.classList.add('loading');
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
    }
}

// Initialize Error Monitor
let errorMonitor;
document.addEventListener('DOMContentLoaded', () => {
    errorMonitor = new ErrorMonitor();
    
    // Add error report button to admin interface
    const adminHeader = document.querySelector('#header');
    if (adminHeader) {
        const reportButton = document.createElement('button');
        reportButton.textContent = '📊 Download Error Report';
        reportButton.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999; padding: 5px 10px; background: #007cba; color: white; border: none; border-radius: 3px; cursor: pointer;';
        reportButton.onclick = () => errorMonitor.downloadErrorReport();
        document.body.appendChild(reportButton);
    }
});

// Export for global access
window.ErrorMonitor = ErrorMonitor;
window.getCsrfToken = getCsrfToken;
window.showLoading = showLoading;
window.hideLoading = hideLoading;