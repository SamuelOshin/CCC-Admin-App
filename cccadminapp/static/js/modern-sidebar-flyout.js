/**
 * Modern Sidebar Flyout System
 * Comprehensive JavaScript for handling sidebar collapse/expand and flyout menus
 * 
 * Features:
 * - Sidebar toggle functionality
 * - Flyout menu positioning and display
 * - Keyboard navigation support
 * - Touch/mobile interactions
 * - State persistence
 * - Performance optimizations
 * - Accessibility compliance
 */

class ModernSidebarFlyout {
    constructor() {
        this.sidebar = null;
        this.toggleBtn = null;
        this.flyoutOverlay = null;
        this.activeFlyout = null;
        this.isCollapsed = false;
        this.isMobile = false;
        this.flyoutTimeout = null;
        this.resizeTimeout = null;
        this.hideTimeout = null; // Single timeout for hiding flyouts
        
        // Configuration
        this.config = {
            breakpoint: 768,
            flyoutDelay: 150,
            flyoutHideDelay: 500, // Increased from 300ms to 500ms for better UX
            animationDuration: 200,
            storageKey: 'sidebar-state',
            flyoutOffset: 10
        };
        
        this.init();
    }
    
    /**
     * Initialize the sidebar flyout system
     */
    init() {
        this.cacheElements();
        
        if (!this.sidebar) {
            return false;
        }
        
        this.loadSavedState();
        this.bindEvents();
        this.setupResponsive();
        this.initializeAccessibility();
        
        return true;
    }
    
    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
        // Core sidebar element
        this.sidebar = document.getElementById('dashboard-sidebar');
        
        // Toggle buttons
        this.toggleBtn = document.getElementById('sidebarToggle');
        this.toggleBtnTop = document.getElementById('sidebarToggleTop');
        
        // Flyout overlay
        this.flyoutOverlay = document.getElementById('flyoutOverlay');
        
        if (!this.sidebar) {
            return;
        }
        
        this.submenuItems = this.sidebar.querySelectorAll('.has-submenu');
        this.flyoutMenus = this.sidebar.querySelectorAll('.flyout-menu');
    }
    
    /**
     * Load saved sidebar state from localStorage
     */
    loadSavedState() {
        try {
            const savedState = localStorage.getItem(this.config.storageKey);
            if (savedState) {
                const state = JSON.parse(savedState);
                this.isCollapsed = state.collapsed || false;
            } else {
                this.isCollapsed = window.innerWidth <= this.config.breakpoint;
            }
            this.updateSidebarState();
        } catch (error) {
            this.isCollapsed = false;
            this.updateSidebarState();
        }
    }
    
    /**
     * Save sidebar state to localStorage
     */
    saveState() {
        try {
            const state = {
                collapsed: this.isCollapsed,
                timestamp: Date.now()
            };
            localStorage.setItem(this.config.storageKey, JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save sidebar state:', error);
        }
    }
    
    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Toggle buttons
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleSidebar();
            });
        }
        
        if (this.toggleBtnTop) {
            this.toggleBtnTop.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleSidebar();
            });
        }
        
        // Submenu items
        this.submenuItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            if (link) {
                // Mouse events
                this.bindMouseEvents(item, link);
                
                // Keyboard events
                this.bindKeyboardEvents(item, link);
                
                // Touch events for mobile
                this.bindTouchEvents(item, link);
            }
        });
        
        // Flyout overlay
        if (this.flyoutOverlay) {
            this.flyoutOverlay.addEventListener('click', () => {
                this.hideFlyout();
            });
        }
        
        // Global keyboard events
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeydown(e);
        });
        
        // Window events
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
        
        // Close flyouts when clicking outside
        document.addEventListener('click', (e) => {
            if (this.activeFlyout && 
                !this.sidebar.contains(e.target) && 
                !this.activeFlyout.contains(e.target)) {
                this.hideFlyout();
            }
        });
    }
    
    /**
     * Bind mouse events for submenu items
     */
    bindMouseEvents(item, link) {
        let showTimeout;
        let mouseEnterPos = { x: 0, y: 0 };
        
        item.addEventListener('mouseenter', (e) => {
            // Track mouse position when entering
            mouseEnterPos.x = e.clientX;
            mouseEnterPos.y = e.clientY;
            
            clearTimeout(this.hideTimeout); // Clear any pending hide operations
            showTimeout = setTimeout(() => {
                this.showFlyout(item);
            }, this.config.flyoutDelay);
        });
        
        item.addEventListener('mouseleave', (e) => {
            const currentMousePos = { x: e.clientX, y: e.clientY };
            const submenuId = item.getAttribute('data-submenu');
            const flyout = document.getElementById(`${submenuId}Flyout`);
            
            // Check if mouse is moving toward the expected flyout area
            const movingToward = this.isMouseMovingTowardFlyoutArea(currentMousePos, mouseEnterPos, item);
            
            if (!movingToward) {
                clearTimeout(showTimeout);
                this.hideTimeout = setTimeout(() => {
                    this.hideFlyout();
                }, this.config.flyoutHideDelay);
            }
        });
    }
    
    /**
     * Bind mouse events to flyout menu to prevent disappearing
     */
    bindFlyoutMouseEvents(flyout) {
        // Create bound methods for this specific flyout
        const handleEnter = (e) => {
            clearTimeout(this.hideTimeout);
            clearTimeout(this.flyoutTimeout);
        };
        
        const handleLeave = (e) => {
            this.hideTimeout = setTimeout(() => {
                this.hideFlyout();
            }, this.config.flyoutHideDelay);
        };
        
        // Store references for cleanup
        flyout._mouseEnterHandler = handleEnter;
        flyout._mouseLeaveHandler = handleLeave;
        
        // Add event listeners
        flyout.addEventListener('mouseenter', handleEnter);
        flyout.addEventListener('mouseleave', handleLeave);
    }
    
    /**
     * Check if the mouse is moving toward the expected flyout area
     * This prevents flyout from disappearing when user tries to move to it
     */
    isMouseMovingTowardFlyoutArea(currentPos, enterPos, navItem) {
        // Calculate mouse movement direction
        const deltaX = currentPos.x - enterPos.x;
        const deltaY = currentPos.y - enterPos.y;
        
        // Get nav item position for reference
        const itemRect = navItem.getBoundingClientRect();
        const sidebarRect = this.sidebar.getBoundingClientRect();
        
        // For collapsed sidebar, flyouts typically appear to the right
        if (this.isCollapsed) {
            // Check if mouse is moving rightward and downward (toward flyout area)
            const isMovingRight = deltaX > 5; // Moved at least 5px right
            const isMovingDown = deltaY > -10; // Allow slight upward movement
            const isNearItemVertically = Math.abs(currentPos.y - itemRect.top) < itemRect.height + 50;
            
            // If mouse is moving right and is vertically near the nav item, likely heading to flyout
            if (isMovingRight && isNearItemVertically) {
                return true;
            }
            
            // Also check if mouse is within expected flyout area (right of sidebar)
            const expectedFlyoutLeft = sidebarRect.right + this.config.flyoutOffset;
            const expectedFlyoutRight = expectedFlyoutLeft + 200; // Approximate flyout width
            const expectedFlyoutTop = itemRect.top - 20;
            const expectedFlyoutBottom = itemRect.bottom + 20;
            
            return currentPos.x >= expectedFlyoutLeft - 20 && 
                   currentPos.x <= expectedFlyoutRight + 20 &&
                   currentPos.y >= expectedFlyoutTop && 
                   currentPos.y <= expectedFlyoutBottom;
        }
        
        return false;
    }
    
    /**
     * Bind keyboard events for accessibility
     */
    bindKeyboardEvents(item, link) {
        link.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Enter':
                case ' ':
                    if (this.isCollapsed) {
                        e.preventDefault();
                        this.showFlyout(item);
                    }
                    break;
                case 'ArrowRight':
                    if (this.isCollapsed) {
                        e.preventDefault();
                        this.showFlyout(item);
                        this.focusFirstFlyoutItem();
                    }
                    break;
                case 'Escape':
                    if (this.activeFlyout) {
                        e.preventDefault();
                        this.hideFlyout();
                        link.focus();
                    }
                    break;
            }
        });
    }
    
    /**
     * Bind touch events for mobile devices
     */
    bindTouchEvents(item, link) {
        let touchStartTime = 0;
        
        link.addEventListener('touchstart', (e) => {
            touchStartTime = Date.now();
        });
        
        link.addEventListener('touchend', (e) => {
            const touchDuration = Date.now() - touchStartTime;
            
            if (this.isCollapsed && touchDuration < 500) {
                e.preventDefault();
                this.showFlyout(item);
            }
        });
    }
    
    /**
     * Handle global keydown events
     */
    handleGlobalKeydown(e) {
        if (e.key === 'Escape' && this.activeFlyout) {
            this.hideFlyout();
        }
        
        // Handle navigation within flyout
        if (this.activeFlyout && this.activeFlyout.classList.contains('show')) {
            this.handleFlyoutNavigation(e);
        }
    }
    
    /**
     * Handle keyboard navigation within flyout menus
     */
    handleFlyoutNavigation(e) {
        const flyoutLinks = this.activeFlyout.querySelectorAll('.flyout-link');
        const currentFocus = document.activeElement;
        const currentIndex = Array.from(flyoutLinks).indexOf(currentFocus);
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = currentIndex < flyoutLinks.length - 1 ? currentIndex + 1 : 0;
                flyoutLinks[nextIndex].focus();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : flyoutLinks.length - 1;
                flyoutLinks[prevIndex].focus();
                break;
                
            case 'ArrowLeft':
                e.preventDefault();
                this.hideFlyout();
                this.focusParentMenuItem();
                break;
                
            case 'Home':
                e.preventDefault();
                flyoutLinks[0].focus();
                break;
                
            case 'End':
                e.preventDefault();
                flyoutLinks[flyoutLinks.length - 1].focus();
                break;
        }
    }
    
    /**
     * Toggle sidebar collapsed/expanded state
     */
    toggleSidebar() {
        this.isCollapsed = !this.isCollapsed;
        this.updateSidebarState();
        this.saveState();
        
        // Hide any active flyouts when expanding
        if (!this.isCollapsed && this.activeFlyout) {
            this.hideFlyout();
        }
        
        this.announceStateChange();
    }
    
    /**
     * Update sidebar visual state
     */
    updateSidebarState() {
        if (this.isCollapsed) {
            this.sidebar.classList.add('collapsed');
            this.toggleBtn?.setAttribute('aria-label', 'Expand sidebar');
            this.toggleBtnTop?.setAttribute('aria-label', 'Expand sidebar');
            this.sidebar.setAttribute('aria-expanded', 'false');
            
            document.body.classList.add('sidebar-collapsed');
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.classList.add('expanded');
            }
        } else {
            this.sidebar.classList.remove('collapsed');
            this.toggleBtn?.setAttribute('aria-label', 'Collapse sidebar');
            this.toggleBtnTop?.setAttribute('aria-label', 'Collapse sidebar');
            this.sidebar.setAttribute('aria-expanded', 'true');
            
            document.body.classList.remove('sidebar-collapsed');
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.classList.remove('expanded');
            }
        }
    }
    
    /**
     * Show flyout menu for a submenu item
     */
    showFlyout(submenuItem) {
        // Only show flyout if sidebar is collapsed
        if (!this.isCollapsed) {
            return;
        }
        
        const submenuType = submenuItem.dataset.submenu;
        const flyoutId = `${submenuType}Flyout`;
        const flyout = document.getElementById(flyoutId);
        
        if (!flyout) {
            return;
        }
        
        // If this flyout is already visible, just ensure it stays visible
        if (this.activeFlyout && this.activeFlyout.id === flyoutId && 
            this.activeFlyout.style.display === 'block') {
            // Clear any pending hide timers
            if (this.hideTimeout) {
                clearTimeout(this.hideTimeout);
                this.hideTimeout = null;
            }
            return;
        }
        
        // Hide any existing flyout (only if it's different)
        if (this.activeFlyout && this.activeFlyout.id !== flyoutId) {
            this.hideFlyout();
        }
        
        this.activeFlyout = flyout;
        this.currentFlyout = flyout;
        
        // Position the flyout
        this.positionFlyout(submenuItem, flyout);
        
        // Show flyout with animation
        requestAnimationFrame(() => {
            flyout.classList.add('show');
            flyout.classList.add('animate-in');
            
            // Show overlay on mobile
            if (this.isMobile && this.flyoutOverlay) {
                this.flyoutOverlay.classList.add('show');
            }
        });
        
        // Add active class to parent item
        const navLink = submenuItem.querySelector('.nav-link');
        if (navLink) {
            navLink.classList.add('flyout-active');
        }
        
        // Bind flyout-specific events
        this.bindFlyoutEvents(flyout);
        
        // Bind flyout mouse events to prevent disappearing
        this.bindFlyoutMouseEvents(flyout);
        
        // Set ARIA attributes
        flyout.setAttribute('aria-hidden', 'false');
        navLink?.setAttribute('aria-expanded', 'true');
    }
    
    /**
     * Hide the active flyout menu
     */
    hideFlyout() {
        if (!this.activeFlyout) {
            return;
        }
        
        const flyout = this.activeFlyout;
        
        // Animate out
        flyout.classList.add('animate-out');
        flyout.classList.remove('animate-in');
        
        setTimeout(() => {
            flyout.classList.remove('show', 'animate-out');
            flyout.setAttribute('aria-hidden', 'true');
        }, this.config.animationDuration);
        
        // Hide overlay
        if (this.flyoutOverlay) {
            this.flyoutOverlay.classList.remove('show');
        }
        
        // Remove active class from parent item
        const activeNavLink = this.sidebar.querySelector('.nav-link.flyout-active');
        if (activeNavLink) {
            activeNavLink.classList.remove('flyout-active');
            activeNavLink.setAttribute('aria-expanded', 'false');
        }
        
        // Clean up
        this.unbindFlyoutEvents(flyout);
        this.activeFlyout = null;
        this.currentFlyout = null;
    }
    
    /**
     * Position flyout menu relative to submenu item
     */
    positionFlyout(submenuItem, flyout) {
        const itemRect = submenuItem.getBoundingClientRect();
        const sidebarRect = this.sidebar.getBoundingClientRect();
        const flyoutRect = flyout.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        if (this.isMobile) {
            flyout.style.top = '0';
            flyout.style.left = '0';
            flyout.style.right = '0';
            flyout.style.bottom = '0';
            flyout.style.transform = 'none';
        } else {
            // Position flyout right next to sidebar with minimal gap
            let left = sidebarRect.right + 2; // Reduced gap to 2px
            let top = itemRect.top;
            
            if (left + flyoutRect.width > viewportWidth) {
                left = sidebarRect.left - flyoutRect.width - 2;
            }
            
            if (top + flyoutRect.height > viewportHeight) {
                top = viewportHeight - flyoutRect.height - 20;
            }
            
            if (top < 20) {
                top = 20;
            }
            
            flyout.style.left = `${left}px`;
            flyout.style.top = `${top}px`;
            flyout.style.zIndex = '1002'; // Ensure flyout is above other elements
        }
    }
    
    /**
     * Bind events specific to flyout menus
     */
    bindFlyoutEvents(flyout) {
        // Close button
        const closeBtn = flyout.querySelector('.flyout-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', this.handleFlyoutClose);
        }
        
        // Prevent closing when clicking inside flyout
        flyout.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    /**
     * Unbind flyout-specific events
     */
    unbindFlyoutEvents(flyout) {
        const closeBtn = flyout.querySelector('.flyout-close');
        if (closeBtn) {
            closeBtn.removeEventListener('click', this.handleFlyoutClose);
        }
        
        // Remove mouse event handlers if they exist
        if (flyout._mouseEnterHandler) {
            flyout.removeEventListener('mouseenter', flyout._mouseEnterHandler);
            delete flyout._mouseEnterHandler;
        }
        if (flyout._mouseLeaveHandler) {
            flyout.removeEventListener('mouseleave', flyout._mouseLeaveHandler);
            delete flyout._mouseLeaveHandler;
        }
    }
    
    /**
     * Handle flyout mouse enter
     */
    handleFlyoutMouseEnter = () => {
        // Clear any pending hide operations when mouse enters the flyout
        clearTimeout(this.hideTimeout);
        clearTimeout(this.flyoutTimeout);
    }
    
    /**
     * Handle flyout mouse leave
     */
    handleFlyoutMouseLeave = () => {
        // Set timeout to hide the flyout when mouse leaves it
        this.hideTimeout = setTimeout(() => {
            this.hideFlyout();
        }, this.config.flyoutHideDelay);
    }
    
    /**
     * Handle flyout close button click
     */
    handleFlyoutClose = (e) => {
        e.preventDefault();
        this.hideFlyout();
        this.focusParentMenuItem();
    }
    
    /**
     * Focus first item in flyout menu
     */
    focusFirstFlyoutItem() {
        if (!this.activeFlyout) return;
        
        const firstLink = this.activeFlyout.querySelector('.flyout-link');
        if (firstLink) {
            setTimeout(() => firstLink.focus(), 100);
        }
    }
    
    /**
     * Focus parent menu item when flyout closes
     */
    focusParentMenuItem() {
        const activeNavLink = this.sidebar.querySelector('.nav-link.flyout-active');
        if (activeNavLink) {
            activeNavLink.focus();
        }
    }
    
    /**
     * Setup responsive behavior
     */
    setupResponsive() {
        this.handleResize();
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= this.config.breakpoint;
        
        // If switching to/from mobile, hide any active flyouts
        if (wasMobile !== this.isMobile && this.activeFlyout) {
            this.hideFlyout();
        }
        
        // Auto-expand sidebar on desktop if collapsed on mobile
        if (!this.isMobile && this.isCollapsed && wasMobile) {
            this.isCollapsed = false;
            this.updateSidebarState();
        }
    }
    
    /**
     * Initialize accessibility features
     */
    initializeAccessibility() {
        // Set initial ARIA attributes
        this.sidebar.setAttribute('role', 'navigation');
        this.sidebar.setAttribute('aria-label', 'Main navigation');
        this.updateSidebarState();
        
        // Set flyout menu attributes
        this.flyoutMenus.forEach(flyout => {
            flyout.setAttribute('aria-hidden', 'true');
            flyout.setAttribute('role', 'menu');
        });
    }
    
    /**
     * Announce state changes for screen readers
     */
    announceStateChange() {
        const message = this.isCollapsed ? 'Sidebar collapsed' : 'Sidebar expanded';
        this.announceToScreenReader(message);
    }
    
    /**
     * Announce message to screen readers
     */
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    /**
     * Debounce utility function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * Public API methods
     */
    
    /**
     * Programmatically show a flyout
     */
    showFlyoutById(flyoutId) {
        const submenuItem = this.sidebar.querySelector(`[data-submenu="${flyoutId}"]`);
        if (submenuItem && this.isCollapsed) {
            this.showFlyout(submenuItem);
        }
    }
    
    /**
     * Programmatically hide flyout
     */
    hideFlyoutMenu() {
        this.hideFlyout();
    }
    
    /**
     * Get current sidebar state
     */
    getState() {
        return {
            collapsed: this.isCollapsed,
            activeFlyout: this.activeFlyout ? this.activeFlyout.id : null,
            isMobile: this.isMobile
        };
    }
    
    /**
     * Destroy the sidebar instance
     */
    destroy() {
        // Remove all event listeners
        this.submenuItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            if (link) {
                link.replaceWith(link.cloneNode(true));
            }
        });
        
        // Clean up
        this.hideFlyout();
        clearTimeout(this.flyoutTimeout);
        clearTimeout(this.resizeTimeout);
        clearTimeout(this.hideTimeout);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        try {
            window.sidebarFlyout = new ModernSidebarFlyout();
        } catch (error) {
            // Create fallback toggle functionality
            const fallbackButtons = document.querySelectorAll('#sidebarToggle, #sidebarToggleTop');
            fallbackButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const sidebar = document.getElementById('dashboard-sidebar');
                    if (sidebar) {
                        sidebar.classList.toggle('collapsed');
                    }
                });
            });
        }
    }, 50);
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernSidebarFlyout;
}