/**
 * Frontend Initialization & Fix Script
 * Loaded on every page to ensure all components work properly
 */

(function() {
  'use strict';
  const IS_DEBUG = Boolean(window.APP_CONFIG && window.APP_CONFIG.DEBUG);

  function devLog(...args) {
    if (IS_DEBUG) {
      console.log(...args);
    }
  }

  function devWarn(...args) {
    if (IS_DEBUG) {
      console.warn(...args);
    }
  }
  
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFrontend);
  } else {
    initializeFrontend();
  }

  function initializeFrontend() {
    devLog('Initializing MediStore Frontend...');
    
    // 1. Verify API Base URL
    if (typeof API_BASE_URL === 'undefined') {
      window.API_BASE_URL =
        window.location.protocol === 'http:' || window.location.protocol === 'https:'
          ? `${window.location.origin}/api`
          : 'http://localhost:8000/api';
      devWarn('API_BASE_URL not defined, using default:', window.API_BASE_URL);
    } else {
      devLog('API_BASE_URL:', window.API_BASE_URL);
    }

    // 2. Initialize theme
    if (document.readyState === 'loading' || !window.themeInitialized) {
      initializeTheme();
      window.themeInitialized = true;
    }

    // 3. Setup event listeners
    setupFormValidation();
    setupLinkPrefixing();
    setupErrorHandlers();
    setupServiceWorker();

    // 4. Ensure functions are available
    ensureFunctionsExist();

    devLog('Frontend initialization complete');
  }

  function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;
    
    if (theme === 'dark') {
      html.setAttribute('data-theme', 'dark');
    } else {
      html.removeAttribute('data-theme');
    }
    devLog('Theme initialized:', theme);
  }

  /**
   * Prevent form submission issues
   */
  function setupFormValidation() {
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function(e) {
        // Prevent double submissions
        if (this.dataset.submitting === 'true') {
          e.preventDefault();
          return false;
        }
        
        // Mark as submitting
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.dataset.originalDisabled = submitBtn.disabled;
          submitBtn.disabled = true;
          this.dataset.submitting = 'true';
          
          // Re-enable after 1 second (safety timeout)
          setTimeout(() => {
            submitBtn.disabled = submitBtn.dataset.originalDisabled === 'true';
            this.dataset.submitting = 'false';
          }, 1000);
        }
      });
    });
  }

  /**
   * Fix relative links and paths
   */
  function setupLinkPrefixing() {
    // Fix image paths
    document.querySelectorAll('img').forEach(img => {
      if (img.src && !img.src.startsWith('http')) {
        if (!img.src.startsWith('/')) {
          img.src = '/' + img.src;
        }
      }
    });

    // Fix script sources
    document.querySelectorAll('script[src]').forEach(script => {
      if (script.src && !script.src.startsWith('http')) {
        if (!script.src.startsWith('/')) {
          script.src = '/' + script.src;
        }
      }
    });

    // Fix stylesheet links
    document.querySelectorAll('link[href]').forEach(link => {
      if (link.href && !link.href.startsWith('http')) {
        if (!link.href.startsWith('/')) {
          link.href = '/' + link.href;
        }
      }
    });
  }

  /**
   * Global error handler
   */
  function setupErrorHandlers() {
    window.addEventListener('error', function(event) {
      console.error('❌ Global Error:', event.error);
      // Don't prevent default - let browser handle it
    });

    window.addEventListener('unhandledrejection', function(event) {
      console.error('❌ Unhandled Promise Rejection:', event.reason);
      event.preventDefault();
    });
  }

  function setupServiceWorker() {
    // Temporarily disabled to prevent stale cached JS/HTML from breaking dynamic pages.
    return;
  }

  /**
   * Ensure critical functions exist
   */
  function ensureFunctionsExist() {
    const requiredFunctions = [
      'setupThemeToggle',
      'setupMobileMenu',
      'checkAuth',
      'getAuthHeader',
      'apiRequest',
      'loginUser',
      'registerUser',
      'logout',
      'toggleTheme',
      'loadTheme'
    ];

    requiredFunctions.forEach(fnName => {
      if (typeof window[fnName] !== 'function') {
        devWarn(`Missing function: ${fnName}`);
      } else {
        devLog(`Function available: ${fnName}`);
      }
    });

    // Provide fallback for missing functions
    if (typeof window.showToast !== 'function') {
      window.showToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          padding: 15px 20px;
          background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
          color: white;
          border-radius: 5px;
          z-index: 10000;
          font-size: 14px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
      };
    }

    if (typeof window.debugLog !== 'function') {
      window.debugLog = function(message, data = null) {
        devLog(`[MediStore] ${message}`, data || '');
      };
    }
  }

  // Expose initialization function for manual re-initialization if needed
  window.reinitializeFrontend = initializeFrontend;

})();
