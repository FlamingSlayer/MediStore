// Global API Configuration
function resolveApiBaseUrl() {
  const isHttp = window.location.protocol === 'http:' || window.location.protocol === 'https:';
  if (!isHttp) {
    return 'http://localhost:8000/api';
  }

  const host = window.location.hostname;
  const port = window.location.port;
  const protocol = window.location.protocol;

  // If frontend is served from Live Server or another local port, route API to Django on :8000.
  if ((host === 'localhost' || host === '127.0.0.1') && port && port !== '8000') {
    return `${protocol}//${host}:8000/api`;
  }

  return `${window.location.origin}/api`;
}

const API_BASE_URL = resolveApiBaseUrl();
const TOKEN_KEY = 'access_token';
const DEBUG = false;

// Debug logging
function debugLog(message, data = null) {
  if (!DEBUG) return;
  console.log(`[MediStore] ${message}`, data || '');
}

// API Endpoints object for reference
const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    LOGOUT: '/auth/logout/'
  },
  PRODUCTS: {
    LIST: '/products/',
    DETAIL: '/products/{id}/',
    FEATURED: '/products/featured/',
    SEARCH: '/products/?search={query}'
  },
  CATEGORIES: {
    LIST: '/categories/'
  },
  CART: {
    GET: '/cart/',
    ADD_ITEM: '/cart/add_item/',
    UPDATE_ITEM: '/cart/update_item/',
    REMOVE_ITEM: '/cart/remove_item/',
    CLEAR: '/cart/clear/'
  },
  ORDERS: {
    LIST: '/orders/',
    CREATE: '/orders/',
    DETAIL: '/orders/{id}/',
    UPDATE_STATUS: '/orders/{id}/update_status/'
  },
  PROFILE: {
    GET: '/profile/',
    UPDATE: '/profile/'
  },
  ADDRESSES: {
    LIST: '/addresses/',
    CREATE: '/addresses/',
    DETAIL: '/addresses/{id}/',
    UPDATE: '/addresses/{id}/',
    DELETE: '/addresses/{id}/'
  },
  PRESCRIPTIONS: {
    LIST: '/prescriptions/',
    CREATE: '/prescriptions/',
    DETAIL: '/prescriptions/{id}/',
    DELETE: '/prescriptions/{id}/'
  }
};

// Application settings
const APP_CONFIG = {
  API_BASE_URL,
  TOKEN_KEY,
  THEME: 'light',
  PAGINATION: {
    LIMIT: 12,
    OFFSET: 0
  },
  TOAST_DURATION: 3000,
  STORE_NAME: 'MediStore',
  DEBUG
};

// Make config globally available
window.API_BASE_URL = API_BASE_URL;
window.TOKEN_KEY = TOKEN_KEY;
window.API_ENDPOINTS = API_ENDPOINTS;
window.APP_CONFIG = APP_CONFIG;
