<template>
  <div>
    <div class="row mb-4 g-3">
      <div class="col-12 col-sm-6 col-lg-3" v-for="stat in statCards" :key="stat.label">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ stat.value }}</h3>
            <p class="text-muted mb-0">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <div class="mb-3" style="max-width: 480px;">
      <div class="input-group">
        <input v-model="searchQuery" class="form-control" placeholder="Search treks or users..." @keyup.enter="runSearch">
        <button class="btn btn-outline-secondary" @click="runSearch">Search</button>
      </div>
      <div v-if="searchQuery && searchResults" class="list-group mt-1 shadow-sm" style="max-height: 260px; overflow-y: auto;">
        <template v-if="searchResults.treks.length === 0 && searchResults.users.length === 0">
          <span class="list-group-item text-muted small">No results found.</span>
        </template>
        <span v-for="t in searchResults.treks" :key="'t'+t.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
          {{ t.name }}
          <span class="badge bg-primary">Trek</span>
        </span>
        <span v-for="u in searchResults.users" :key="'u'+u.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
          {{ u.name }}
          <span class="badge bg-secondary">{{ u.role }}</span>
        </span>
      </div>
    </div>

    <ul class="nav nav-pills mb-3 flex-wrap gap-1">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='treks'}" href="#" @click.prevent="tab='treks'">Treks</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='staff'}" href="#" @click.prevent="tab='staff'">Staff</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='users'}" href="#" @click.prevent="tab='users'">Users</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='bookings'}" href="#" @click.prevent="tab='bookings'">Bookings</a></li>
    </ul>

    <!-- TREKS TAB -->
    <div v-if="tab==='treks'">
      <button class="btn btn-primary mb-3" @click="showTrekForm = !showTrekForm">
        {{ showTrekForm ? 'Cancel' : '+ New Trek' }}
      </button>

      <form v-if="showTrekForm" @submit.prevent="submitTrek" class="card card-body mb-3" novalidate>
        <div class="row g-2">
          <div class="col-12 col-md-4"><input v-model="trekForm.name" class="form-control" placeholder="Trek Name" required></div>
          <div class="col-12 col-md-4"><input v-model="trekForm.location" class="form-control" placeholder="Location" required></div>
          <div class="col-12 col-md-4">
            <select v-model="trekForm.difficulty" class="form-select" required>
              <option value="">Difficulty</option>
              <option>Easy</option><option>Moderate</option><option>Hard</option>
            </select>
          </div>
          <div class="col-12 col-md-4"><input v-model.number="trekForm.duration_days" type="number" class="form-control" placeholder="Duration (days)" required></div>
          <div class="col-12 col-md-4"><input v-model.number="trekForm.total_slots" type="number" class="form-control" placeholder="Total Slots" required></div>
          <div class="col-12 col-md-4">
            <label class="form-label small text-muted mb-1">Start Date <span class="text-danger">*</span></label>
            <input v-model="trekForm.start_date" type="date" class="form-control" :class="{ 'is-invalid': trekFormSubmitted && !trekForm.start_date }" required>
            <div class="invalid-feedback">Start date is required.</div>
          </div>
          <div class="col-12 col-md-4">
            <label class="form-label small text-muted mb-1">End Date <span class="text-danger">*</span></label>
            <input v-model="trekForm.end_date" type="date" class="form-control" :class="{ 'is-invalid': trekFormSubmitted && !trekForm.end_date }" required>
            <div class="invalid-feedback">End date is required.</div>
          </div>
          <div v-if="trekFormSubmitted && trekForm.start_date && trekForm.end_date && trekForm.end_date <= trekForm.start_date" class="col-12">
            <div class="alert alert-danger py-1 mb-0 small">End date must be after start date.</div>
          </div>
          <div class="col-12 col-md-4"><button class="btn btn-success w-100" type="submit">Create Trek</button></div>
        </div>
      </form>

      <div class="table-responsive">
        <table class="table table-striped table-hover bg-white">
          <thead>
            <tr>
              <th>Name</th><th>Location</th><th>Difficulty</th><th>Slots</th><th>Status</th><th>Staff</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in treks" :key="t.id">
              <td>{{ t.name }}</td>
              <td>{{ t.location }}</td>
              <td>{{ t.difficulty }}</td>
              <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
              <td>
                <template v-if="t.status === 'Completed'">
                  <span class="badge bg-primary">Completed</span>
                </template>
                <template v-else>
                  <select :value="t.status" @change="changeStatus(t, $event.target.value)" class="form-select form-select-sm">
                    <option>Pending</option><option>Approved</option><option>Open</option><option>Ongoing</option><option>Closed</option><option>Completed</option>
                  </select>
                </template>
              </td>
              <td>
                <select :value="t.assigned_staff_id || ''" @change="assign(t, $event.target.value)" class="form-select form-select-sm">
                  <option value="">Unassigned</option>
                  <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </td>
              <td><button class="btn btn-sm btn-danger" @click="removeTrek(t.id)">Delete</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- STAFF TAB -->
    <div v-if="tab==='staff'">
      <button class="btn btn-primary mb-3" @click="showStaffForm = !showStaffForm">
        {{ showStaffForm ? 'Cancel' : '+ New Staff' }}
      </button>

      <form v-if="showStaffForm" @submit.prevent="submitStaff" class="card card-body mb-3">
        <div class="row g-2">
          <div class="col-12 col-md-3"><input v-model="staffForm.name" class="form-control" placeholder="Name" required></div>
          <div class="col-12 col-md-3"><input v-model="staffForm.email" type="email" class="form-control" placeholder="Email" required></div>
          <div class="col-12 col-md-3"><input v-model="staffForm.password" type="password" class="form-control" placeholder="Password" required></div>
          <div class="col-12 col-md-3"><button class="btn btn-success w-100" type="submit">Create Staff</button></div>
        </div>
      </form>

      <div class="table-responsive">
        <table class="table table-striped bg-white">
          <thead><tr><th>Name</th><th>Email</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="s in staff" :key="s.id">
              <td>{{ s.name }}</td><td>{{ s.email }}</td>
              <td><span :class="s.active ? 'badge bg-success' : 'badge bg-secondary'">{{ s.active ? 'Active' : 'Inactive' }}</span></td>
              <td><button class="btn btn-sm btn-outline-warning" @click="toggleUser(s)">{{ s.active ? 'Deactivate' : 'Activate' }}</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- USERS TAB -->
    <div v-if="tab==='users'">
      <div class="table-responsive">
        <table class="table table-striped bg-white">
          <thead><tr><th>Name</th><th>Email</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.name }}</td><td>{{ u.email }}</td>
              <td><span :class="u.active ? 'badge bg-success' : 'badge bg-secondary'">{{ u.active ? 'Active' : 'Inactive' }}</span></td>
              <td><button class="btn btn-sm btn-outline-warning" @click="toggleUser(u)">{{ u.active ? 'Deactivate' : 'Activate' }}</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- BOOKINGS TAB -->
    <div v-if="tab==='bookings'">
      <div class="table-responsive">
        <table class="table table-striped bg-white">
          <thead><tr><th>User</th><th>Trek</th><th>Status</th><th>Date</th></tr></thead>
          <tbody>
            <tr v-for="b in bookings" :key="b.id">
              <td>{{ b.user_name }}</td><td>{{ b.trek_name }}</td><td>{{ b.status }}</td><td>{{ b.booking_date }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'

const tab = ref('treks')
const errorMsg = ref('')
const searchQuery = ref('')
const searchResults = ref(null)

async function runSearch() {
  if (!searchQuery.value.trim()) { searchResults.value = null; return }
  try {
    searchResults.value = await api.adminSearch(searchQuery.value.trim())
  } catch (e) {
    errorMsg.value = e.message
  }
}

const stats = ref({ total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 })
const treks = ref([])
const staff = ref([])
const users = ref([])
const bookings = ref([])

const showTrekForm = ref(false)
const trekFormSubmitted = ref(false)
const trekForm = ref({ name: '', location: '', difficulty: '', duration_days: null, total_slots: null, start_date: '', end_date: '' })

const showStaffForm = ref(false)
const staffForm = ref({ name: '', email: '', password: '' })

const statCards = computed(() => [
  { label: 'Treks', value: stats.value.total_treks },
  { label: 'Users', value: stats.value.total_users },
  { label: 'Staff', value: stats.value.total_staff },
  { label: 'Bookings', value: stats.value.total_bookings },
])

async function loadAll() {
  stats.value = await api.dashboardStats()
  treks.value = await api.listTreks()
  staff.value = await api.listStaff()
  users.value = await api.listUsers()
  bookings.value = await api.allBookings()
}

onMounted(loadAll)

async function submitTrek() {
  trekFormSubmitted.value = true
  if (!trekForm.value.start_date || !trekForm.value.end_date) return
  if (trekForm.value.end_date <= trekForm.value.start_date) return
  errorMsg.value = ''
  try {
    await api.createTrek(trekForm.value)
    trekForm.value = { name: '', location: '', difficulty: '', duration_days: null, total_slots: null, start_date: '', end_date: '' }
    trekFormSubmitted.value = false
    showTrekForm.value = false
    await loadAll()
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function removeTrek(id) {
  if (!confirm('Delete this trek?')) return
  errorMsg.value = ''
  try {
    await api.deleteTrek(id)
    await loadAll()
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function changeStatus(trek, newStatus) {
  errorMsg.value = ''
  try {
    await api.updateTrek(trek.id, { status: newStatus })
    await loadAll()
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function assign(trek, staffId) {
  errorMsg.value = ''
  try {
    await api.assignStaff(trek.id, staffId ? parseInt(staffId) : null)
    await loadAll()
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function submitStaff() {
  errorMsg.value = ''
  try {
    await api.createStaff(staffForm.value)
    staffForm.value = { name: '', email: '', password: '' }
    showStaffForm.value = false
    await loadAll()
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function toggleUser(user) {
  errorMsg.value = ''
  try {
    await api.toggleActive(user.id)
    await loadAll()
  } catch (e) {
    errorMsg.value = e.message
  }
}
</script>