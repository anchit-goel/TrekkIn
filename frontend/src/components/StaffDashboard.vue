<template>
  <div>
    <div class="row mb-4 g-3">
      <div class="col-12 col-md-4">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ stats.total_treks }}</h3>
            <p class="text-muted mb-0">Assigned Treks</p>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ stats.total_trekkers }}</h3>
            <p class="text-muted mb-0">Registered Trekkers</p>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ stats.ongoing_treks }}</h3>
            <p class="text-muted mb-0">Ongoing Treks</p>
          </div>
        </div>
      </div>
    </div>

    <ul class="nav nav-pills nav-pills-custom mb-3">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='treks'}" href="#" @click.prevent="tab='treks'">My Treks</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='participants'}" href="#" @click.prevent="selectParticipantsTab">Participants</a></li>
    </ul>

    <div v-if="loading" class="text-muted">Loading...</div>
    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <!-- MY TREKS TAB -->
    <div v-if="tab==='treks' && !loading">
      <div v-if="treks.length === 0" class="text-muted">No treks assigned to you yet.</div>

      <div class="row g-3">
        <div class="col-12 col-md-6" v-for="t in treks" :key="t.id">
          <div class="card shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="card-title mb-0">{{ t.name }}</h5>
                <span class="badge" :class="statusBadge(t.status)">{{ t.status }}</span>
              </div>
              <p class="text-muted small mb-2">{{ t.location }} · {{ t.duration_days }} days · {{ t.difficulty }}</p>
              <p class="mb-2"><strong>{{ t.registered }}</strong> / {{ t.total_slots }} trekkers registered</p>

              <div class="row g-2 align-items-center">
                <div class="col-6">
                  <label class="form-label small text-muted mb-1">Available Slots</label>
                  <input type="number" class="form-control form-control-sm"
                         :value="t.available_slots" min="0" :max="t.total_slots"
                         @change="updateSlots(t, $event.target.value)">
                </div>
                <div class="col-6">
                  <label class="form-label small text-muted mb-1">Trek Status</label>
                  <select class="form-select form-select-sm" :value="t.status" @change="updateStatus(t, $event.target.value)">
                    <option>Open</option>
                    <option>Closed</option>
                    <option>Ongoing</option>
                    <option>Completed</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PARTICIPANTS TAB -->
    <div v-if="tab==='participants' && !loading">
      <div v-if="treks.length === 0" class="text-muted">No treks assigned — no participants to show.</div>

      <div v-else>
        <select class="form-select mb-3" style="max-width: 300px;" v-model="selectedTrekId" @change="loadParticipants">
          <option v-for="t in treks" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>

        <input v-model="participantSearch" class="form-control mb-3" placeholder="Search by name..." style="max-width: 300px;">

        <div v-if="participants.length === 0" class="text-muted">No bookings for this trek yet.</div>

        <div class="table-responsive">
          <table v-if="participants.length" class="table table-striped bg-white">
            <thead>
              <tr><th>Name</th><th>Email</th><th>Booking Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="p in filteredParticipants" :key="p.booking_id">
                <td>{{ p.name }}</td>
                <td>{{ p.email }}</td>
                <td><span :class="statusBadge(p.status)" class="badge">{{ p.status }}</span></td>
                <td>
                  <button class="btn btn-sm btn-outline-success me-1" v-if="p.status==='Booked'" @click="markBooking(p, 'Completed')">Mark Completed</button>
                  <button class="btn btn-sm btn-outline-danger" v-if="p.status==='Booked'" @click="markBooking(p, 'Cancelled')">Cancel</button>
                  <button class="btn btn-sm btn-outline-secondary" v-if="p.status==='Completed' || p.status==='Cancelled'" @click="markBooking(p, 'Booked')">Revert to Booked</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'

const tab = ref('treks')
const loading = ref(false)
const errorMsg = ref('')

const stats = ref({ total_treks: 0, total_trekkers: 0, ongoing_treks: 0 })
const treks = ref([])
const participants = ref([])
const selectedTrekId = ref(null)
const participantSearch = ref('')

const filteredParticipants = computed(() => {
  const q = participantSearch.value.toLowerCase()
  if (!q) return participants.value
  return participants.value.filter(p => p.name.toLowerCase().includes(q))
})

async function loadAll() {
  loading.value = true
  errorMsg.value = ''
  try {
    stats.value = await api.staffDashboard()
    treks.value = await api.staffTreks()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)

function selectParticipantsTab() {
  tab.value = 'participants'
  if (treks.value.length && !selectedTrekId.value) {
    selectedTrekId.value = treks.value[0].id
  }
  if (selectedTrekId.value) loadParticipants()
}

async function loadParticipants() {
  if (!selectedTrekId.value) return
  errorMsg.value = ''
  try {
    participants.value = await api.staffTrekParticipants(selectedTrekId.value)
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function updateSlots(trek, value) {
  const slots = parseInt(value)
  errorMsg.value = ''
  try {
    await api.staffUpdateTrek(trek.id, { available_slots: slots })
    trek.available_slots = slots
  } catch (e) {
    errorMsg.value = e.message
    await loadAll()
  }
}

async function updateStatus(trek, status) {
  errorMsg.value = ''
  try {
    await api.staffUpdateTrek(trek.id, { status })
    trek.status = status
  } catch (e) {
    errorMsg.value = e.message
    await loadAll()
  }
}

async function markBooking(participant, status) {
  errorMsg.value = ''
  try {
    await api.staffUpdateBooking(participant.booking_id, status)
    await loadAll()
    await loadParticipants()
  } catch (e) {
    errorMsg.value = e.message
  }
}

function statusBadge(status) {
  const map = {
    Open: 'bg-success', Closed: 'bg-secondary', Ongoing: 'bg-warning text-dark',
    Completed: 'bg-primary', Booked: 'bg-info text-dark', Cancelled: 'bg-danger'
  }
  return map[status] || 'bg-secondary'
}
</script>