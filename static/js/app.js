// Global variables (try to get from config.js, fall back to defaults)
if (typeof API_BASE_URL === 'undefined') {
  window.API_BASE_URL = 'http://127.0.0.1:8000/api';
}
if (typeof TOKEN_KEY === 'undefined') {
  window.TOKEN_KEY = 'access_token';
}

// ==================== Utility Functions ====================

/**
 * Query selector shorthand
 */
function $(selector) {
  return document.querySelector(selector);
}

/**
 * Query selector all shorthand
 */
function $$(selector) {
  return document.querySelectorAll(selector);
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('en-IN', options);
}

/**
 * Get user initials from name
 */
function getInitials(firstName, lastName) {
  return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
}

/**
 * Format currency
 */
function formatCurrency(amount) {
  return `₹${amount.toFixed(2)}`;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
    <span>${message}</span>
  `;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, duration);
}

/**
 * Unified client-side error handler for UI pages.
 */
function reportClientError(context, error, userMessage = 'Something went wrong. Please try again.') {
  const details = error && error.message ? error.message : error;
  debugLog(`[ClientError] ${context}`, details || 'Unknown error');

  if (window.APP_CONFIG && window.APP_CONFIG.DEBUG) {
    console.error(`[ClientError] ${context}`, error);
  }

  if (typeof showToast === 'function' && userMessage) {
    showToast(userMessage, 'error', 4000);
  }
}

window.reportClientError = reportClientError;

/**
 * Check if user is authenticated
 */
function checkAuth() {
  const token = localStorage.getItem(TOKEN_KEY);
  const user = localStorage.getItem('user');

  if (token && user) {
    try {
      const userData = JSON.parse(user);
      const userNameElem = document.getElementById('user-name');
      if (userNameElem) {
        userNameElem.textContent = userData.first_name || userData.username;
      }

      // Hide guest nav, show user nav
      const guestNav = document.getElementById('guest-nav');
      const userNav = document.getElementById('user-nav');
      if (guestNav) guestNav.style.display = 'none';
      if (userNav) userNav.style.display = 'flex';

      // Update Dashboard Link Based on User Role
      const dashLinks = document.querySelectorAll('a[href="dashboard.html"], a[href="/dashboard/"]');
      if (userData.is_staff || userData.is_superuser) {
        dashLinks.forEach(link => {
            link.href = 'admin.html';
            if(link.textContent === 'Dashboard') link.textContent = 'Admin Dashboard';
        });
      }

      // Setup logout
      const logoutBtn = document.getElementById('logoutBtn');
      if (logoutBtn && !logoutBtn.dataset.listenerAdded) {
        logoutBtn.addEventListener('click', logout);
        logoutBtn.dataset.listenerAdded = 'true';
      }

      return true;
    } catch (error) {
      console.error('Error parsing user data:', error);
      // fallback
    }
} else {
    // Show guest nav, hide user nav
    const guestNav = document.getElementById('guest-nav');
    const userNav = document.getElementById('user-nav');
    if (guestNav) guestNav.style.display = 'flex';
    if (userNav) userNav.style.display = 'none';

    return false;
  }
}

/**
 * Logout user
 */
function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem('user');
  window.location.href = 'index.html';
}

/**
 * Get authorization header with proper Token format
 */
function getAuthHeader() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    return {};
  }

  // Ensure token is in "Token <value>" format
  if (token.startsWith('Token ')) {
    return { 'Authorization': token };
  }

  if (token.startsWith('Bearer ')) {
    // Convert Bearer to Token format
    const tokenValue = token.slice(7);
    return { 'Authorization': `Token ${tokenValue}` };
  }

  // If it's just the token value, add Token prefix
  return { 'Authorization': `Token ${token}` };
}

// ==================== API Helper Functions ====================

/**
 * API request wrapper with comprehensive error handling
 */
async function apiRequest(endpoint, method = 'GET', body = null, isFormData = false) {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
      method,
      headers: {
        ...getAuthHeader()
      }
    };

    // Don't set Content-Type for FormData (browser will set it)
    if (!isFormData) {
      options.headers['Content-Type'] = 'application/json';
    }

    if (body) {
      if (isFormData) {
        options.body = body; // FormData object
      } else {
        options.body = JSON.stringify(body);
      }
    }


    const response = await fetch(url, options);
    const contentType = response.headers.get('content-type') || '';
    let data = null;

    try {
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else if (contentType.includes('text')) {
        data = await response.text();
      }
    } catch (parseError) {
      console.warn('Could not parse response body:', parseError);
    }


    if (!response.ok) {
      const errorMessage = 
        data?.error || 
        data?.message || 
        data?.detail ||
        (typeof data === 'string' ? data : null) ||
        `API request failed (${response.status})`;
      throw new Error(errorMessage);
    }

    return { success: true, data, status: response.status };
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    return { success: false, error: error.message, data: null };
  }
}

/**
 * Login user with proper error handling
 */
async function loginUser(username, password) {
  const result = await apiRequest('/auth/login/', 'POST', { username, password });
  
  if (result.success && result.data) {
    const token = result.data.token;
    const user = result.data.user;
    
    // Store token and user info
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return { success: true, data: result.data };
  }
  
  return { success: false, error: result.error || 'Login failed' };
}

/**
 * Register new user with proper error handling
 */
async function registerUser(userData) {
  const result = await apiRequest('/auth/register/', 'POST', userData);
  
  if (result.success && result.data) {
    const token = result.data.token;
    const user = result.data.user;
    
    // Store token and user info
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return { success: true, data: result.data };
  }
  
  return { success: false, error: result.error || 'Registration failed' };
}

/**
 * Get user profile
 */
async function getUserProfile() {
  return await apiRequest('/profile/');
}

/**
 * Update user profile
 */
async function updateUserProfile(profileData) {
  return await apiRequest('/profile/', 'PUT', profileData);
}

/**
 * Get all products
 */
async function getProducts(params = {}) {
  let url = '/products/';
  const queryParams = new URLSearchParams(params);
  if (queryParams.toString()) {
    url += '?' + queryParams.toString();
  }
  return await apiRequest(url);
}

/**
 * Get single product
 */
async function getProduct(productId) {
  return await apiRequest(`/products/${productId}/`);
}

/**
 * Get featured products
 */
async function getFeaturedProducts() {
  return await apiRequest('/products/featured/');
}

/**
 * Search products
 */
async function searchProducts(query) {
  return await apiRequest(`/products/?search=${encodeURIComponent(query)}`);
}

/**
 * Get all categories
 */
async function getCategories() {
  return await apiRequest('/categories/');
}

/**
 * Get user cart
 */
async function getCart() {
  return await apiRequest('/cart/');
}

/**
 * Add item to cart
 */
async function addToCart(productId, quantity = 1) {
  return await apiRequest('/cart/add_item/', 'POST', {
    product_id: productId,
    quantity
  });
}

/**
 * Update cart item quantity
 */
async function updateCartItem(cartItemId, quantity) {
  return await apiRequest('/cart/update_item/', 'POST', {
    item_id: cartItemId,
    quantity
  });
}

/**
 * Remove item from cart
 */
async function removeFromCart(cartItemId) {
  return await apiRequest('/cart/remove_item/', 'POST', {
    item_id: cartItemId
  });
}

/**
 * Clear entire cart
 */
async function clearCart() {
  return await apiRequest('/cart/clear/', 'POST');
}

/**
 * Get all orders
 */
async function getOrders() {
  return await apiRequest('/orders/');
}

/**
 * Get single order
 */
async function getOrder(orderId) {
  return await apiRequest(`/orders/${orderId}/`);
}

/**
 * Create order from cart
 */
async function createOrder(addressId, paymentMethod = 'cod') {
  return await apiRequest('/orders/', 'POST', {
    address_id: addressId,
    payment_method: paymentMethod
  });
}

/**
 * Update order status (admin only)
 */
async function updateOrderStatus(orderId, status) {
  return await apiRequest(`/orders/${orderId}/update_status/`, 'POST', {
    status
  });
}

/**
 * Get user addresses
 */
async function getAddresses() {
  return await apiRequest('/addresses/');
}

/**
 * Get single address
 */
async function getAddress(addressId) {
  return await apiRequest(`/addresses/${addressId}/`);
}

/**
 * Create new address
 */
async function createAddress(addressData) {
  return await apiRequest('/addresses/', 'POST', addressData);
}

/**
 * Update address
 */
async function updateAddress(addressId, addressData) {
  return await apiRequest(`/addresses/${addressId}/`, 'PUT', addressData);
}

/**
 * Delete address
 */
async function deleteAddress(addressId) {
  return await apiRequest(`/addresses/${addressId}/`, 'DELETE');
}

/**
 * Get user prescriptions
 */
async function getPrescriptions() {
  return await apiRequest('/prescriptions/');
}

/**
 * Upload prescription
 */
async function uploadPrescription(formData) {
  try {
    const response = await fetch(`${API_BASE_URL}/prescriptions/`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Upload failed');
    }

    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Delete prescription
 */
async function deletePrescription(prescriptionId) {
  return await apiRequest(`/prescriptions/${prescriptionId}/`, 'DELETE');
}

// ==================== UI Helper Functions ====================

/**
 * Toggle theme (dark/light mode)
 */
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  
  if (isDark) {
    html.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
  } else {
    html.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  }

  updateThemeIcon();
}

function updateThemeIcon() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) {
    return;
  }

  const icon = themeToggle.querySelector('i');
  if (!icon) {
    return;
  }

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
}

/**
 * Load theme preference
 */
function loadTheme() {
  const theme = localStorage.getItem('theme') || 'light';
  const html = document.documentElement;
  
  if (theme === 'dark') {
    html.setAttribute('data-theme', 'dark');
  } else {
    html.removeAttribute('data-theme');
  }

  updateThemeIcon();
}

/**
 * Setup theme toggle button
 */
function setupThemeToggle() {
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle && !themeToggle.dataset.listenerAdded) {
    themeToggle.addEventListener('click', toggleTheme);
    themeToggle.dataset.listenerAdded = 'true';
  }
  loadTheme();
}

/**
 * Setup mobile menu
 */
function setupMobileMenu() {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.getElementById('navLinks');
  
  if (mobileMenuBtn && navLinks && !mobileMenuBtn.dataset.listenerAdded) {
    mobileMenuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
    mobileMenuBtn.dataset.listenerAdded = 'true';
  }
}

/**
 * Format product for display
 */
function formatProduct(product) {
  return {
    ...product,
    displayPrice: formatCurrency(product.discount_price || product.price),
    originalPrice: product.price,
    discountedPrice: product.discount_price,
    hasDiscount: product.discount_percentage > 0,
    displayDiscount: product.discount_percentage ? `${product.discount_percentage}%` : null
  };
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
  setupThemeToggle();
  setupMobileMenu();
  checkAuth();
});

// ==================== Export for use in modules ====================
// These can be imported in other scripts or used directly
