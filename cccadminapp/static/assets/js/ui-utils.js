/**
 * UI Utilities Module
 * Consolidates alert, loading screen, and other UI-related functions
 */

(function(window) {
    'use strict';

    const UIUtils = {
        /**
         * Show an alert message
         * @param {string} message - The alert message
         * @param {string} type - Alert type (success, warning, danger, info)
         * @param {HTMLElement} container - Container to insert alert (optional)
         * @param {number} autoHideDuration - Auto-hide duration in ms (default: 5000)
         */
        showAlert: function(message, type = 'info', container = null, autoHideDuration = 5000) {
            // Find container if not provided
            if (!container) {
                container = document.querySelector('.card-body') || document.querySelector('main') || document.body;
            }

            if (!container) return;

            // Remove existing alerts of the same type
            const existingAlerts = container.querySelectorAll(`.alert-${type}`);
            existingAlerts.forEach(alert => alert.remove());

            // Create alert element
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-2`;
            alertDiv.setAttribute('role', 'alert');
            alertDiv.innerHTML = `
                <i class="bi bi-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            // Insert at the beginning of container
            container.insertBefore(alertDiv, container.firstChild);

            // Auto-hide after duration
            if (autoHideDuration > 0) {
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.classList.remove('show');
                        setTimeout(() => alertDiv.remove(), 150);
                    }
                }, autoHideDuration);
            }

            return alertDiv;
        },

        /**
         * Get Bootstrap icon for alert type
         * @param {string} type - Alert type
         * @returns {string} - Icon name
         */
        getAlertIcon: function(type) {
            const icons = {
                'success': 'check-circle',
                'warning': 'exclamation-triangle',
                'danger': 'exclamation-triangle',
                'error': 'exclamation-triangle',
                'info': 'info-circle'
            };
            return icons[type] || 'info-circle';
        },

        /**
         * Auto-hide alerts after a duration
         * @param {number} duration - Duration in milliseconds
         */
        autoHideAlerts: function(duration = 5000) {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(function(alert) {
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.style.display = 'none';
                    }
                }, duration);
            });
        },

        /**
         * Show loading screen
         */
        showLoading: function() {
            const loadingScreen = document.getElementById('loading');
            if (loadingScreen) {
                loadingScreen.style.display = 'flex';
            }
        },

        /**
         * Hide loading screen
         */
        hideLoading: function() {
            const loadingScreen = document.getElementById('loading');
            if (loadingScreen) {
                loadingScreen.style.display = 'none';
            }
        },

        /**
         * Initialize loading screen for navigation
         * Consolidated logic to avoid duplication
         */
        initLoadingScreen: function() {
            const loadingScreen = document.getElementById('loading');
            if (!loadingScreen) return;

            // Helper function to check if element is form-related
            const isFormRelated = function(element) {
                return element && (
                    element.tagName === 'BUTTON' ||
                    element.tagName === 'INPUT' ||
                    element.type === 'submit' ||
                    element.closest('form') ||
                    document.querySelector('form.submitting')
                );
            };

            // Show loading screen on page unload (but not for form submissions)
            window.addEventListener('beforeunload', function(event) {
                const activeElement = document.activeElement;
                
                // Skip loading screen for form submissions
                if (isFormRelated(activeElement)) {
                    return;
                }

                // Show loading screen for regular navigation only
                loadingScreen.style.display = 'flex';
            });

            // Hide loading screen when page is fully loaded
            window.addEventListener('load', function() {
                loadingScreen.style.display = 'none';
            });

            // Hide loading screen when page becomes visible
            document.addEventListener('visibilitychange', function() {
                if (!document.hidden) {
                    loadingScreen.style.display = 'none';
                }
            });

            // Hide loading screen when navigating back to the page
            window.addEventListener('pageshow', function(event) {
                loadingScreen.style.display = 'none';
            });

            // Handle link clicks (but not for form submissions or sidebar toggles)
            document.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', function(event) {
                    // Don't show for sidebar toggle links
                    if (this.hasAttribute('data-bs-toggle') && this.getAttribute('data-bs-toggle') === 'collapse') {
                        return;
                    }

                    // Don't show for form-related links
                    if (this.closest('form') || this.getAttribute('type') === 'submit') {
                        return;
                    }

                    // Don't show for anchor links that don't navigate
                    if (this.getAttribute('href') === '#') {
                        return;
                    }

                    // Don't show for external links or new tabs
                    if (this.getAttribute('target') === '_blank' || this.hostname !== window.location.hostname) {
                        return;
                    }

                    // Show loading screen for regular navigation links
                    loadingScreen.style.display = 'flex';
                });
            });

            // Handle form submissions - don't interfere with their loading states
            document.querySelectorAll('form').forEach(form => {
                form.addEventListener('submit', function() {
                    // Forms handle their own loading states
                });
            });
        },

        /**
         * Initialize form validation (Bootstrap 5)
         */
        initFormValidation: function() {
            const forms = document.querySelectorAll('.needs-validation');
            
            Array.prototype.slice.call(forms).forEach(function(form) {
                form.addEventListener('submit', function(event) {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            });
        }
    };

    // Expose to global scope
    window.UIUtils = UIUtils;

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            UIUtils.autoHideAlerts();
            UIUtils.initLoadingScreen();
        });
    } else {
        // DOM already loaded
        UIUtils.autoHideAlerts();
        UIUtils.initLoadingScreen();
    }

})(window);
