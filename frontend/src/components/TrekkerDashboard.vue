<template>
  <div>
    <ul class="nav nav-pills nav-pills-custom mb-3">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='browse'}" href="#" @click.prevent="tab='browse'">Browse Treks</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='bookings'}" href="#" @click.prevent="tab='bookings'">My Bookings</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='history'}" href="#" @click.prevent="tab='history'">Trekking History</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='profile'}" href="#" @click.prevent="tab='profile'">My Profile</a></li>
    </ul>

    <!-- BROWSE TAB -->
    <div v-if="tab==='browse'">
      <div class="row g-2 mb-3">
        <div class="col-md-4">
          <input v-model="filters.search" class="form-control" placeholder="Search treks...">
        </div>
        <div class="col-md-4">
          <select v-model="filters.difficulty" class="form-select">
            <option value="">Any Difficulty</option>
            <option>Easy</option><option>Moderate</option><option>Hard</option>
          </select>
        </div>
        <div class="col-md-4">
          <select v-model="filters.location" class="form-select">
            <option value="">Any Location</option>
            <option v-for="loc in locations" :key="loc">{{ loc }}</option>
          </select>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-4" v-for="t in filteredTreks" :key="t.id">
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
    <div v-if="tab==='bookings'">
      <table class="table table-striped bg-white">
        <thead><tr><th>Trek</th><th>Status</th><th>Booking Date</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="b in mockBookings" :key="b.id">
            <td>{{ b.trek_name }}</td>
            <td><span class="badge" :class="statusBadge(b.status)">{{ b.status }}</span></td>
            <td>{{ b.booking_date }}</td>
            <td>
              <button class="btn btn-sm btn-outline-danger" v-if="b.status==='Booked'" @click="cancelBooking(b)">Cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- HISTORY TAB -->
    <div v-if="tab==='history'">
      <table class="table table-striped bg-white">
        <thead><tr><th>Trek</th><th>Location</th><th>Completed On</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="h in mockHistory" :key="h.id">
            <td>{{ h.trek_name }}</td>
            <td>{{ h.location }}</td>
            <td>{{ h.date }}</td>
            <td><span class="badge bg-primary">{{ h.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PROFILE TAB -->
    <div v-if="tab==='profile'">
      <div class="card shadow-sm" style="max-width: 500px;">
        <div class="card-body">
          <h5 class="card-title mb-3">My Profile</h5>
          <div class="mb-3">
            <label class="form-label small text-muted">Full Name</label>
            <input v-model="profile.name" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label small text-muted">Email</label>
            <input v-model="profile.email" class="form-control" disabled>
          </div>
          <div class="mb-3">
            <label class="form-label small text-muted">Phone</label>
            <input v-model="profile.phone" class="form-control" placeholder="Optional">
          </div>
          <button class="btn btn-primary" @click="saveProfile">Save Changes</button>
          <span v-if="profileSaved" class="text-success ms-2 small">Saved ✓</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tab = ref('browse')

const filters = ref({ search: '', difficulty: '', location: '' })

const mockOpenTreks = ref([
  { id: 1, name: 'Everest Base Camp', location: 'Nepal', difficulty: 'Hard', duration_days: 12, available_slots: 3 },
  { id: 2, name: 'Valley of Flowers', location: 'Uttarakhand', difficulty: 'Moderate', duration_days: 5, available_slots: 5 },
  { id: 3, name: 'Hampta Pass', location: 'Himachal Pradesh', difficulty: 'Easy', duration_days: 4, available_slots: 0 },
])

const locations = computed(() => [...new Set(mockOpenTreks.value.map(t => t.location))])

const filteredTreks = computed(() => mockOpenTreks.value.filter(t => {
  const matchesSearch = t.name.toLowerCase().includes(filters.value.search.toLowerCase())
  const matchesDifficulty = !filters.value.difficulty || t.difficulty === filters.value.difficulty
  const matchesLocation = !filters.value.location || t.location === filters.value.location
  return matchesSearch && matchesDifficulty && matchesLocation
}))

const mockBookings = ref([
  { id: 1, trek_name: 'Everest Base Camp', status: 'Booked', booking_date: '2026-07-20' },
])

const mockHistory = ref([
  { id: 1, trek_name: 'Kedarkantha Trek', location: 'Uttarakhand', date: '2026-03-15', status: 'Completed' },
])

const profile = ref({ name: 'Test User', email: 'trekker@test.com', phone: '' })
const profileSaved = ref(false)

function diffBadge(d) {
  return { Easy: 'bg-success', Moderate: 'bg-warning text-dark', Hard: 'bg-danger' }[d] || 'bg-secondary'
}
function statusBadge(s) {
  return { Booked: 'bg-info text-dark', Cancelled: 'bg-danger', Completed: 'bg-primary' }[s] || 'bg-secondary'
}

function bookTrek(trek) {
  if (confirm(`Confirm booking for "${trek.name}"?`)) {
    mockBookings.value.push({
      id: mockBookings.value.length + 1,
      trek_name: trek.name,
      status: 'Booked',
      booking_date: new Date().toISOString().split('T')[0]
    })
    trek.available_slots -= 1
    tab.value = 'bookings'
  }
}

function cancelBooking(booking) {
  if (confirm(`Cancel booking for "${booking.trek_name}"?`)) {
    booking.status = 'Cancelled'
    const trek = mockOpenTreks.value.find(t => t.name === booking.trek_name)
    if (trek) trek.available_slots += 1
  }
}

function saveProfile() {
  profileSaved.value = true
  setTimeout(() => profileSaved.value = false, 2000)
}
</script>