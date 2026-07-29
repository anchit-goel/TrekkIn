<template>
  <div>
    <div class="row mb-4">
      <div class="col-md-3" v-for="stat in statCards" :key="stat.label">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ stat.value }}</h3>
            <p class="text-muted mb-0">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <ul class="nav nav-pills mb-3">
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

      <form v-if="showTrekForm" @submit.prevent="submitTrek" class="card card-body mb-3">
        <div class="row g-2">
          <div class="col-md-4"><input v-model="trekForm.name" class="form-control" placeholder="Trek Name" required></div>
          <div class="col-md-4"><input v-model="trekForm.location" class="form-control" placeholder="Location" required></div>
          <div class="col-md-4">
            <select v-model="trekForm.difficulty" class="form-select" required>
              <option value="">Difficulty</option>
              <option>Easy</option><option>Moderate</option><option>Hard</option>
            </select>
          </div>
          <div class="col-md-4"><input v-model.number="trekForm.duration_days" type="number" class="form-control" placeholder="Duration (days)" required></div>
          <div class="col-md-4"><input v-model.number="trekForm.total_slots" type="number" class="form-control" placeholder="Total Slots" required></div>
          <div class="col-md-4"><button class="btn btn-success w-100" type="submit">Create Trek</button></div>
        </div>
      </form>

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
              <select :value="t.status" @change="changeStatus(t, $event.target.value)" class="form-select form-select-sm">
                <option>Pending</option><option>Approved</option><option>Open</option><option>Closed</option><option>Completed</option>
              </select>
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

    <!-- STAFF TAB -->
    <div v-if="tab==='staff'">
      <button class="btn btn-primary mb-3" @click="showStaffForm = !showStaffForm">
        {{ showStaffForm ? 'Cancel' : '+ New Staff' }}
      </button>

      <form v-if="showStaffForm" @submit.prevent="submitStaff" class="card card-body mb-3">
        <div class="row g-2">
          <div class="col-md-3"><input v-model="staffForm.name" class="form-control" placeholder="Name" required></div>
          <div class="col-md-3"><input v-model="staffForm.email" type="email" class="form-control" placeholder="Email" required></div>
          <div class="col-md-3"><input v-model="staffForm.password" type="password" class="form-control" placeholder="Password" required></div>
          <div class="col-md-3"><button class="btn btn-success w-100" type="submit">Create Staff</button></div>
        </div>
      </form>

      <table class="table table-striped bg-white">
        <thead><tr><th>Name</th><th>Email</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id">
            <td>{{ s.name }}</td><td>{{ s.email }}</td>
            <td><span :class="s.active ? 'badge bg-success' : 'badge bg-secondary'">{{ s.active ? 'Active' : 'Inactive' }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- USERS TAB -->
    <div v-if="tab==='users'">
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

    <!-- BOOKINGS TAB -->
    <div v-if="tab==='bookings'">
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'

const tab = ref('treks')
const errorMsg = ref('')

const stats = ref({ total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 })
const treks = ref([])
const staff = ref([])
const users = ref([])
const bookings = ref([])

const showTrekForm = ref(false)
const trekForm = ref({ name: '', location: '', difficulty: '', duration_days: null, total_slots: null })

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
  errorMsg.value = ''
  try {
    await api.createTrek(trekForm.value)
    trekForm.value = { name: '', location: '', difficulty: '', duration_days: null, total_slots: null }
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