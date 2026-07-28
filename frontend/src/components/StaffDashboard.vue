<template>
  <div>
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ mockTreks.length }}</h3>
            <p class="text-muted mb-0">Assigned Treks</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ totalTrekkers }}</h3>
            <p class="text-muted mb-0">Registered Trekkers</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center shadow-sm stat-card">
          <div class="card-body">
            <h3>{{ ongoingCount }}</h3>
            <p class="text-muted mb-0">Ongoing Treks</p>
          </div>
        </div>
      </div>
    </div>

    <ul class="nav nav-pills nav-pills-custom mb-3">
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='treks'}" href="#" @click.prevent="tab='treks'">My Treks</a></li>
      <li class="nav-item"><a class="nav-link" :class="{active: tab==='participants'}" href="#" @click.prevent="tab='participants'">Participants</a></li>
    </ul>

    <!-- MY TREKS TAB -->
    <div v-if="tab==='treks'">
      <div class="row g-3">
        <div class="col-md-6" v-for="t in mockTreks" :key="t.id">
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
                  <input type="number" class="form-control form-control-sm" v-model.number="t.available_slots">
                </div>
                <div class="col-6">
                  <label class="form-label small text-muted mb-1">Trek Status</label>
                  <select class="form-select form-select-sm" v-model="t.status">
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
    <div v-if="tab==='participants'">
      <select class="form-select mb-3" style="max-width: 300px;" v-model="selectedTrekId">
        <option v-for="t in mockTreks" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>

      <table class="table table-striped bg-white">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Booking Status</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in currentParticipants" :key="p.id">
            <td>{{ p.name }}</td>
            <td>{{ p.email }}</td>
            <td><span :class="statusBadge(p.status)" class="badge">{{ p.status }}</span></td>
            <td>
              <button class="btn btn-sm btn-outline-success me-1">Mark Completed</button>
              <button class="btn btn-sm btn-outline-danger">Cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tab = ref('treks')

const mockTreks = ref([
  { id: 1, name: 'Everest Base Camp', location: 'Nepal', difficulty: 'Hard', duration_days: 12, total_slots: 10, available_slots: 3, registered: 7, status: 'Open' },
  { id: 2, name: 'Valley of Flowers', location: 'Uttarakhand', difficulty: 'Moderate', duration_days: 5, total_slots: 15, available_slots: 5, registered: 10, status: 'Ongoing' },
])

const selectedTrekId = ref(1)

const mockParticipants = {
  1: [
    { id: 1, name: 'Ravi Kumar', email: 'ravi@test.com', status: 'Booked' },
    { id: 2, name: 'Sneha Rao', email: 'sneha@test.com', status: 'Booked' },
  ],
  2: [
    { id: 3, name: 'Amit Shah', email: 'amit@test.com', status: 'Booked' },
  ]
}

const currentParticipants = computed(() => mockParticipants[selectedTrekId.value] || [])

const totalTrekkers = computed(() => mockTreks.value.reduce((sum, t) => sum + t.registered, 0))
const ongoingCount = computed(() => mockTreks.value.filter(t => t.status === 'Ongoing').length)

function statusBadge(status) {
  const map = {
    Open: 'bg-success', Closed: 'bg-secondary', Ongoing: 'bg-warning text-dark',
    Completed: 'bg-primary', Booked: 'bg-info text-dark', Cancelled: 'bg-danger'
  }
  return map[status] || 'bg-secondary'
}
</script>