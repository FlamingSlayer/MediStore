/* Admin page controller extracted from inline template script.
   Keeping this in an external file avoids inline-script parsing/caching issues. */

const DEBUG_ADMIN = true;

function adminLog(...args) {
  if (DEBUG_ADMIN) {
    console.log('[ADMIN]', ...args);
  }
}

function adminError(...args) {
  console.error('[ADMIN ERROR]', ...args);
}

const adminCache = {
  products: [],
  orders: [],
  users: [],
};

function buildAuthHeaders(extraHeaders = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    return { ...extraHeaders };
  }

  const normalized = token.startsWith('Token ') || token.startsWith('Bearer ')
    ? token
    : `Token ${token}`;

  return {
    Authorization: normalized,
    ...extraHeaders,
  };
}

function toCsvValue(value) {
  const text = String(value ?? '');
  return `"${text.replace(/"/g, '""')}"`;
}

function downloadCsv(filename, headers, rows) {
  const lines = [headers.map(toCsvValue).join(',')];
  rows.forEach((row) => lines.push(row.map(toCsvValue).join(',')));
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.download = filename;
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function renderSimpleTable(targetId, headers, rowsHtml) {
  const target = document.getElementById(targetId);
  if (!target) return;

  const th = headers.map((h) => `<th style="padding:12px;">${h}</th>`).join('');
  target.innerHTML = `
    <div class="table-responsive">
      <table class="table" style="width:100%; border-collapse:collapse; text-align:left;">
        <thead><tr style="border-bottom:2px solid #ddd; background:#f9f9f9;">${th}</tr></thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    </div>
  `;
}

function renderOrdersChart(points) {
  const ctx = document.getElementById('ordersChart');
  if (!ctx || typeof Chart === 'undefined') return;
  if (window.ordersChart) {
    window.ordersChart.destroy();
  }

  window.ordersChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: points.map((p) => p.month),
      datasets: [
        {
          label: 'Orders',
          data: points.map((p) => p.order_count),
          borderColor: '#ff6a00',
          backgroundColor: 'rgba(255,106,0,0.16)',
          tension: 0.35,
          yAxisID: 'y'
        },
        {
          label: 'Revenue (INR)',
          data: points.map((p) => p.revenue),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16,185,129,0.15)',
          tension: 0.35,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { position: 'left' },
        y1: { position: 'right', grid: { drawOnChartArea: false } }
      }
    }
  });
}

function showTab(tabId) {
  document.querySelectorAll('.tab-content').forEach((tab) => tab.classList.remove('active'));
  document.querySelectorAll('.dashboard-nav .nav-item').forEach((item) => item.classList.remove('active'));

  const selected = document.getElementById(`${tabId}Tab`);
  if (selected) selected.classList.add('active');
  localStorage.setItem('admin_active_tab', tabId);

  const activeBtn = document.querySelector(`.dashboard-nav button[onclick="showTab('${tabId}')"]`);
  if (activeBtn) activeBtn.classList.add('active');
}

async function loadAdminData(showFeedback = false) {
  try {
    if (showFeedback && typeof showToast === 'function') {
      showToast('Refreshing admin data...', 'info', 1200);
    }

    const headers = buildAuthHeaders();

    const statsRes = await fetch(`${API_BASE_URL}/admin/stats/`, { headers });
    if (statsRes.ok) {
      const statsRaw = await statsRes.json();
      const stats = Array.isArray(statsRaw) ? statsRaw[0] : statsRaw;
      const mapping = {
        'admin-total-orders': stats?.total_orders,
        'admin-total-users': stats?.total_users,
        'admin-pending-prescriptions': stats?.pending_prescriptions,
        'admin-pending-orders': stats?.pending_orders,
        'admin-revenue': stats?.revenue,
      };
      Object.entries(mapping).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = String(value ?? 0);
      });
    }

    const productsRes = await fetch(`${API_BASE_URL}/products/`, { headers });
    if (productsRes.ok) {
      const payload = await productsRes.json();
      adminCache.products = Array.isArray(payload) ? payload : (payload.results || []);

      const rows = adminCache.products.map((p) => `
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:12px;">#${p.id}</td>
          <td style="padding:12px;">${p.name || ''}</td>
          <td style="padding:12px;">${p.brand || ''}</td>
          <td style="padding:12px;">₹${p.price || 0}</td>
          <td style="padding:12px;">${p.stock || 0}</td>
          <td style="padding:12px;"><button class="btn btn-sm" onclick="deleteProduct(${p.id})">Delete</button></td>
        </tr>
      `).join('');
      renderSimpleTable('adminProductsList', ['ID', 'Name', 'Brand', 'Price', 'Stock', 'Actions'], rows);

      const lowStock = adminCache.products.filter((p) => Number(p.stock || 0) > 0 && Number(p.stock || 0) < 10).length;
      const outStock = adminCache.products.filter((p) => Number(p.stock || 0) === 0).length;
      const lowStockEl = document.getElementById('admin-low-stock');
      const outStockEl = document.getElementById('admin-out-stock');
      if (lowStockEl) lowStockEl.textContent = String(lowStock);
      if (outStockEl) outStockEl.textContent = String(outStock);
    }

    const ordersRes = await fetch(`${API_BASE_URL}/orders/`, { headers });
    if (ordersRes.ok) {
      const payload = await ordersRes.json();
      adminCache.orders = Array.isArray(payload) ? payload : (payload.results || []);

      const rows = adminCache.orders.map((o) => `
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:12px;">#${o.id}</td>
          <td style="padding:12px;">${new Date(o.placed_at || o.created_at || Date.now()).toLocaleDateString()}</td>
          <td style="padding:12px;">₹${o.total_amount || 0}</td>
          <td style="padding:12px;"><span class="status-badge status-${String(o.status || '').toLowerCase()}">${o.status || ''}</span></td>
        </tr>
      `).join('');
      renderSimpleTable('adminOrdersList', ['Order', 'Date', 'Amount', 'Status'], rows);

      const recentRows = adminCache.orders.slice(0, 5).map((o) => `
        <tr>
          <td>#${o.id}</td>
          <td>${new Date(o.placed_at || o.created_at || Date.now()).toLocaleDateString()}</td>
          <td><span class="status-badge status-${String(o.status || '').toLowerCase()}">${o.status || ''}</span></td>
          <td>₹${o.total_amount || 0}</td>
        </tr>
      `).join('') || '<tr><td colspan="4">No recent orders found.</td></tr>';
      const recentEl = document.getElementById('recentOrdersList');
      if (recentEl) recentEl.innerHTML = recentRows;
    }

    const usersRes = await fetch(`${API_BASE_URL}/admin/users/`, { headers });
    if (usersRes.ok) {
      const payload = await usersRes.json();
      adminCache.users = Array.isArray(payload) ? payload : (payload.results || []);

      const rows = adminCache.users.map((u) => `
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:12px;">#${u.id}</td>
          <td style="padding:12px;">${u.username || ''}</td>
          <td style="padding:12px;">${u.email || ''}</td>
          <td style="padding:12px;">${u.is_staff ? 'Admin' : 'Customer'}</td>
          <td style="padding:12px;">${new Date(u.date_joined || Date.now()).toLocaleDateString()}</td>
        </tr>
      `).join('');
      renderSimpleTable('adminUsersList', ['ID', 'Username', 'Email', 'Role', 'Joined'], rows);
    }

    const prescriptionsRes = await fetch(`${API_BASE_URL}/prescriptions/?status=pending`, { headers });
    if (prescriptionsRes.ok) {
      const payload = await prescriptionsRes.json();
      const items = Array.isArray(payload) ? payload : (payload.results || []);
      const html = items.map((p) => `
        <div class="summary-card" style="margin-bottom:12px;">
          <p><strong>User:</strong> ${p.user_name || 'N/A'} | <strong>Status:</strong> ${p.status || ''}</p>
          <p><a href="${p.file || '#'}" target="_blank" rel="noopener">Preview Prescription File</a></p>
        </div>
      `).join('') || '<p>No pending prescriptions.</p>';
      const rxEl = document.getElementById('adminPrescriptionsList');
      if (rxEl) rxEl.innerHTML = html;
    }

    const chartRes = await fetch(`${API_BASE_URL}/admin/stats/chart/`, { headers });
    if (chartRes.ok) {
      const chartData = await chartRes.json();
      renderOrdersChart(chartData || []);
    }

    const updatedEl = document.getElementById('adminLastUpdated');
    if (updatedEl) {
      updatedEl.textContent = `Last updated: ${new Date().toLocaleTimeString('en-IN')}`;
    }

    if (showFeedback && typeof showToast === 'function') {
      showToast('Admin data refreshed', 'success');
    }
  } catch (error) {
    adminError('loadAdminData failed:', error);
    if (typeof reportClientError === 'function') {
      reportClientError('Error loading admin data', error, 'Unable to load admin dashboard data.');
    }
  }
}

function exportProductsCsv() {
  const rows = (adminCache.products || []).map((p) => [p.id, p.name, p.brand || '', p.price, p.stock, p.prescription_required]);
  downloadCsv('medistore_products.csv', ['ID', 'Name', 'Brand', 'Price', 'Stock', 'Prescription Required'], rows);
}

function exportOrdersCsv() {
  const rows = (adminCache.orders || []).map((o) => [o.id, o.status, o.total_amount, o.placed_at || o.created_at || '', o.return_requested ? 'Yes' : 'No']);
  downloadCsv('medistore_orders.csv', ['Order ID', 'Status', 'Amount', 'Placed At', 'Return Requested'], rows);
}

function exportUsersCsv() {
  const rows = (adminCache.users || []).map((u) => [u.id, u.username, u.email || '', u.is_staff ? 'Admin' : 'Customer', u.date_joined || '']);
  downloadCsv('medistore_users.csv', ['ID', 'Username', 'Email', 'Role', 'Joined'], rows);
}

async function deleteProduct(id) {
  if (!confirm(`Are you sure you want to delete Product #${id}?`)) return;
  const res = await fetch(`${API_BASE_URL}/products/${id}/`, {
    method: 'DELETE',
    headers: buildAuthHeaders(),
  });
  if (res.ok) {
    loadAdminData();
  } else {
    alert('Failed to delete product.');
  }
}

function showAddProductModal() {
  const modal = document.getElementById('productModal');
  const form = document.getElementById('productForm');
  const idField = document.getElementById('productId');
  if (form) form.reset();
  if (idField) idField.value = '';
  if (modal) modal.style.display = 'flex';
}

function showEditProductModal(id, name, brand, price, stock, rx) {
  const modal = document.getElementById('productModal');
  const idField = document.getElementById('productId');
  const nameField = document.getElementById('productName');
  const brandField = document.getElementById('productBrand');
  const priceField = document.getElementById('productPrice');
  const stockField = document.getElementById('productStock');
  const rxField = document.getElementById('productRx');

  if (idField) idField.value = id;
  if (nameField) nameField.value = name || '';
  if (brandField) brandField.value = brand || '';
  if (priceField) priceField.value = price || 0;
  if (stockField) stockField.value = stock || 0;
  if (rxField) rxField.checked = rx === 'true';
  if (modal) modal.style.display = 'flex';
}

function closeProductModal() {
  const modal = document.getElementById('productModal');
  if (modal) modal.style.display = 'none';
}

async function markAsShipped(orderId) {
  const res = await fetch(`${API_BASE_URL}/orders/${orderId}/update_status/`, {
    method: 'POST',
    headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ status: 'shipped' }),
  });
  if (res.ok) loadAdminData();
}

async function approveReturn(orderId) {
  const res = await fetch(`${API_BASE_URL}/orders/${orderId}/approve_return/`, {
    method: 'POST',
    headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
  });
  if (res.ok) loadAdminData();
}

function openPrescriptionQueue() {
  showTab('prescriptions');
}

function runShippingAutoFlow() { showToast('Shipping flow available after data load', 'info'); }
function printShippingManifest() { window.print(); }
function bulkUpdateOrderStatus() { showToast('Select specific order and update status', 'info'); }
function toggleSelectAllOrders() {}
function setAllOrderCheckboxes() {}

window.showTab = showTab;
window.loadAdminData = loadAdminData;
window.exportProductsCsv = exportProductsCsv;
window.exportOrdersCsv = exportOrdersCsv;
window.exportUsersCsv = exportUsersCsv;
window.showAddProductModal = showAddProductModal;
window.showEditProductModal = showEditProductModal;
window.closeProductModal = closeProductModal;
window.deleteProduct = deleteProduct;
window.markAsShipped = markAsShipped;
window.approveReturn = approveReturn;
window.openPrescriptionQueue = openPrescriptionQueue;
window.runShippingAutoFlow = runShippingAutoFlow;
window.printShippingManifest = printShippingManifest;
window.bulkUpdateOrderStatus = bulkUpdateOrderStatus;
window.toggleSelectAllOrders = toggleSelectAllOrders;
window.setAllOrderCheckboxes = setAllOrderCheckboxes;

window.diagAdmin = async function diagAdmin() {
  console.log('API_BASE_URL:', API_BASE_URL);
  console.log('Token exists:', !!localStorage.getItem(TOKEN_KEY));
  try {
    const r = await fetch(`${API_BASE_URL}/admin/stats/`, { headers: buildAuthHeaders() });
    console.log('/admin/stats =>', r.status);
  } catch (e) {
    console.error('diagAdmin failed:', e);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (typeof checkAdminAccess === 'function' && !checkAdminAccess()) {
    return;
  }

  const savedTab = localStorage.getItem('admin_active_tab') || 'overview';
  showTab(savedTab);
  loadAdminData();

  const refreshBtn = document.getElementById('refreshAdminBtn');
  if (refreshBtn) refreshBtn.addEventListener('click', () => loadAdminData(true));

  const form = document.getElementById('productForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('productId')?.value;
      const payload = {
        name: document.getElementById('productName')?.value,
        brand: document.getElementById('productBrand')?.value,
        price: document.getElementById('productPrice')?.value,
        stock: document.getElementById('productStock')?.value,
        prescription_required: !!document.getElementById('productRx')?.checked,
        category: 1,
        description: `${document.getElementById('productName')?.value || 'Product'} description`,
        dosage: 'Standard'
      };

      const method = id ? 'PATCH' : 'POST';
      const url = id ? `${API_BASE_URL}/products/${id}/` : `${API_BASE_URL}/products/`;
      const res = await fetch(url, {
        method,
        headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        closeProductModal();
        loadAdminData();
      } else {
        alert('Failed to save product.');
      }
    });
  }

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await fetch(`${API_BASE_URL}/auth/logout/`, { method: 'POST', headers: buildAuthHeaders() });
      } catch (_) {
      } finally {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem('user');
        window.location.href = 'login.html';
      }
    });
  }
});
