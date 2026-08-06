<template>
  <div>
    <ul class="nav nav-pills nav-pills-custom mb-3">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='browse'}" href="#" @click.prevent="switchTab('browse')">Browse Treks</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='bookings'}" href="#" @click.prevent="switchTab('bookings')">My Bookings</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='history'}" href="#" @click.prevent="switchTab('history')">Trekking History</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='profile'}" href="#" @click.prevent="switchTab('profile')">My Profile</a></li>
    </ul>

    <div v-if="loading" class="text-muted">Loading...</div>
    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <!-- BROWSE TAB -->
    <div v-if="tab==='browse' && !loading">
      <div class="row g-2 mb-3">
        <div class="col-12 col-md-4">
          <input v-model="filters.search" class="form-control" placeholder="Search treks...">
        </div>
        <div class="col-12 col-md-4">
          <select v-model="filters.difficulty" class="form-select">
            <option value="">Any Difficulty</option>
            <option>Easy</option><option>Moderate</option><option>Hard</option>
          </select>
        </div>
        <div class="col-12 col-md-4">
          <select v-model="filters.location" class="form-select">
            <option value="">Any Location</option>
            <option v-for="loc in locations" :key="loc">{{ loc }}</option>
          </select>
        </div>
      </div>

      <div v-if="openTreks.length === 0" class="text-muted">No open treks available right now.</div>

      <div class="row g-3">
        <div class="col-12 col-md-4" v-for="t in filteredTreks" :key="t.id">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column">
              <div class="d-flex justify-content-between mb-2">
                <h5 class="card-title mb-0">{{ t.name }}</h5>
                <span class="badge" :class="diffBadge(t.difficulty)">{{ t.difficulty }}</span>
              </div>
              <p class="text-muted small mb-2">{{ t.location }} · {{ t.duration_days }} days</p>
              <p class="mb-3">{{ t.available_slots }} slots left</p>
              <button class="btn btn-primary mt-auto" :disabled="t.available_slots === 0" @click="bookTrek(t)">
                {{ t.available_slots === 0 ? 'Full' : 'Book Trek' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MY BOOKINGS TAB -->
    <div v-if="tab==='bookings' && !loading">
      <div v-if="bookings.length === 0" class="text-muted">You have no bookings yet.</div>

      <div class="table-responsive">
        <table v-if="bookings.length" class="table table-striped bg-white">
          <thead><tr><th>Trek</th><th>Location</th><th>Status</th><th>Booking Date</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="b in bookings" :key="b.id">
              <td>{{ b.trek_name }}</td>
              <td>{{ b.location }}</td>
              <td><span class="badge" :class="statusBadge(b.status)">{{ b.status }}</span></td>
              <td>{{ b.booking_date.split('T')[0] }}</td>
              <td>
                <button class="btn btn-sm btn-outline-danger" v-if="b.status==='Booked'" @click="cancelBooking(b)">Cancel</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- HISTORY TAB -->
    <div v-if="tab==='history' && !loading">
      <div v-if="history.length === 0" class="text-muted">No completed treks yet.</div>

      <div class="table-responsive">
        <table v-if="history.length" class="table table-striped bg-white">
          <thead><tr><th>Trek</th><th>Location</th><th>Completed On</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="h in history" :key="h.trek_name + h.date">
              <td>{{ h.trek_name }}</td>
              <td>{{ h.location }}</td>
              <td>{{ h.date.split('T')[0] }}</td>
              <td><span class="badge bg-primary">{{ h.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <button class="btn btn-outline-primary mt-3" @click="startExport">Export Booking History (CSV, emailed to you)</button>
       <p v-if="exportMsg" class="text-success mt-2 small">{{ exportMsg }}</p>
    </div>

    <!-- PROFILE TAB -->
    <div v-if="tab==='profile' && !loading">
      <div class="card shadow-sm" style="max-width: 500px;">
        <div class="card-body">
          <h5 class="card-title mb-3">My Profile</h5>
          <div class="mb-3">
            <label class="form-label small text-muted">Full Name</label>
            <input v-model="profile.name" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label small text-muted">Email</label>
            <input :value="profile.email" class="form-control" disabled>
          </div>
          <button class="btn btn-primary" @click="saveProfile">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'
import { inject } from 'vue'

const showToast = inject('showToast')
const tab = ref('browse')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const filters = ref({ search: '', difficulty: '', location: '' })
const openTreks = ref([])
const bookings = ref([])
const history = ref([])
const profile = ref({ name: '', email: '' })

const locations = computed(() => [...new Set(openTreks.value.map(t => t.location))])

const filteredTreks = computed(() => openTreks.value.filter(t => {
  const matchesSearch = t.name.toLowerCase().includes(filters.value.search.toLowerCase())
  const matchesDifficulty = !filters.value.difficulty || t.difficulty === filters.value.difficulty
  const matchesLocation = !filters.value.location || t.location === filters.value.location
  return matchesSearch && matchesDifficulty && matchesLocation
}))

function clearMsgs() {
  errorMsg.value = ''
  successMsg.value = ''
}

async function loadBrowse() {
  openTreks.value = await api.browseTreks()
}
async function loadBookings() {
  bookings.value = await api.myBookings()
}
async function loadHistory() {
  history.value = await api.trekHistory()
}
async function loadProfile() {
  profile.value = await api.getProfile()
}

async function switchTab(t) {
  tab.value = t
  clearMsgs()
  loading.value = true
  try {
    if (t === 'browse') await loadBrowse()
    else if (t === 'bookings') await loadBookings()
    else if (t === 'history') await loadHistory()
    else if (t === 'profile') await loadProfile()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(() => switchTab('browse'))

async function bookTrek(trek) {
  if (!confirm(`Confirm booking for "${trek.name}"?`)) return
  try {
    await api.bookTrek(trek.id)
    showToast(`Booked "${trek.name}" successfully!`, 'success')
    await loadBrowse()
  } catch (e) {
    showToast(e.message, 'error')
  }
}

async function cancelBooking(booking) {
  if (!confirm(`Cancel booking for "${booking.trek_name}"?`)) return
  try {
    await api.cancelBooking(booking.id)
    showToast('Booking cancelled.', 'success')
    await loadBookings()
  } catch (e) {
    showToast(e.message, 'error')
  }
}

async function saveProfile() {
  clearMsgs()
  try {
    const res = await api.updateProfile(profile.value.name)
    successMsg.value = 'Profile updated.'
  } catch (e) {
    errorMsg.value = e.message
  }
}

function diffBadge(d) {
  return { Easy: 'bg-success', Moderate: 'bg-warning text-dark', Hard: 'bg-danger' }[d] || 'bg-secondary'
}
function statusBadge(s) {
  return { Booked: 'bg-info text-dark', Cancelled: 'bg-danger', Completed: 'bg-primary' }[s] || 'bg-secondary'
}

const exportMsg = ref('')

async function startExport() {
  exportMsg.value = ''
  try {
    const res = await api.triggerExport()
    exportMsg.value = 'Export started — check your email shortly.'
  } catch (e) {
    errorMsg.value = e.message
  }
}
</script>

