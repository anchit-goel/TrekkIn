const API_BASE = 'http://127.0.0.1:5000/api'

function authHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
}

async function handle(res) {
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Request failed')
  return data
}

export const api = {
  // auth
  login: (email, password) =>
    fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    }).then(handle),

  register: (name, email, password) =>
    fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    }).then(handle),

  me: () =>
    fetch(`${API_BASE}/auth/me`, { headers: authHeaders() }).then(handle),

  // admin
  dashboardStats: () =>
    fetch(`${API_BASE}/admin/dashboard`, { headers: authHeaders() }).then(handle),

  listTreks: () =>
    fetch(`${API_BASE}/admin/treks`, { headers: authHeaders() }).then(handle),

  createTrek: (trek) =>
    fetch(`${API_BASE}/admin/treks`, {
      method: 'POST', headers: authHeaders(), body: JSON.stringify(trek)
    }).then(handle),

  updateTrek: (id, trek) =>
    fetch(`${API_BASE}/admin/treks/${id}`, {
      method: 'PUT', headers: authHeaders(), body: JSON.stringify(trek)
    }).then(handle),

  deleteTrek: (id) =>
    fetch(`${API_BASE}/admin/treks/${id}`, {
      method: 'DELETE', headers: authHeaders()
    }).then(handle),

  assignStaff: (trekId, staffId) =>
    fetch(`${API_BASE}/admin/treks/${trekId}/assign`, {
      method: 'PUT', headers: authHeaders(), body: JSON.stringify({ staff_id: staffId })
    }).then(handle),

  listStaff: () =>
    fetch(`${API_BASE}/admin/staff`, { headers: authHeaders() }).then(handle),

  createStaff: (staff) =>
    fetch(`${API_BASE}/admin/staff`, {
      method: 'POST', headers: authHeaders(), body: JSON.stringify(staff)
    }).then(handle),

  listUsers: () =>
    fetch(`${API_BASE}/admin/users`, { headers: authHeaders() }).then(handle),

  toggleActive: (userId) =>
    fetch(`${API_BASE}/admin/users/${userId}/toggle-active`, {
      method: 'PUT', headers: authHeaders()
    }).then(handle),

  adminSearch: (query) =>
    fetch(`${API_BASE}/admin/search?q=${encodeURIComponent(query)}`, { headers: authHeaders() }).then(handle),

    // staff
  staffDashboard: () =>
    fetch(`${API_BASE}/staff/dashboard`, { headers: authHeaders() }).then(handle),

  staffTreks: () =>
    fetch(`${API_BASE}/staff/treks`, { headers: authHeaders() }).then(handle),

  staffUpdateTrek: (trekId, payload) =>
    fetch(`${API_BASE}/staff/treks/${trekId}`, {
      method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload)
    }).then(handle),

  staffTrekParticipants: (trekId) =>
    fetch(`${API_BASE}/staff/treks/${trekId}/participants`, { headers: authHeaders() }).then(handle),

  staffUpdateBooking: (bookingId, status) =>
    fetch(`${API_BASE}/staff/bookings/${bookingId}`, {
      method: 'PUT', headers: authHeaders(), body: JSON.stringify({ status })
 }).then(handle),

  allBookings: () =>
    fetch(`${API_BASE}/admin/bookings`, { headers: authHeaders() }).then(handle),

  // trekker
  browseTreks: () =>
    fetch(`${API_BASE}/user/treks`, { headers: authHeaders() }).then(handle),

  bookTrek: (trekId) =>
    fetch(`${API_BASE}/user/bookings`, {
      method: 'POST', headers: authHeaders(), body: JSON.stringify({ trek_id: trekId })
    }).then(handle),

  myBookings: () =>
    fetch(`${API_BASE}/user/bookings`, { headers: authHeaders() }).then(handle),

  cancelBooking: (bookingId) =>
    fetch(`${API_BASE}/user/bookings/${bookingId}/cancel`, {
      method: 'PUT', headers: authHeaders()
    }).then(handle),

  trekHistory: () =>
    fetch(`${API_BASE}/user/history`, { headers: authHeaders() }).then(handle),

  getProfile: () =>
    fetch(`${API_BASE}/user/profile`, { headers: authHeaders() }).then(handle),

  updateProfile: (name) =>
    fetch(`${API_BASE}/user/profile`, {
      method: 'PUT', headers: authHeaders(), body: JSON.stringify({ name })
    }).then(handle),

  triggerExport: () =>
    fetch(`${API_BASE}/user/export`, { method: 'POST', headers: authHeaders() }).then(handle),

  exportStatus: (taskId) =>
    fetch(`${API_BASE}/user/export/${taskId}`, { headers: authHeaders() }).then(handle),
}
