<template>
  <div>
    <!-- Fixed top nav shown when logged in -->
    <nav v-if="loggedIn" class="navbar navbar-dark bg-dark px-4 top-navbar sticky-top">
      <span class="navbar-brand mb-0">🏔️ Trekking Management</span>
      <div class="d-flex align-items-center">
        <span class="text-white-50 me-3">
          <span class="badge bg-primary text-uppercase me-2">{{ userRole }}</span>
          {{ userName }}
        </span>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <!-- Auth screen -->
    <div v-if="!loggedIn" class="auth-wrapper">
      <div class="auth-card">
        <div class="card-header-custom">
          <h2 class="mb-1">🏔️ Trekking Management</h2>
          <p class="mb-0 opacity-75">Plan. Book. Explore.</p>
        </div>

        <div class="card-body-custom">
          <ul class="nav nav-pills nav-pills-custom mb-4 justify-content-center gap-2">
            <li class="nav-item">
              <a class="nav-link" :class="{active: view==='login'}" href="#" @click.prevent="switchView('login')">Login</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{active: view==='register'}" href="#" @click.prevent="switchView('register')">Register</a>
            </li>
          </ul>

          <form v-if="view==='login'" @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label small text-muted">Email</label>
              <input v-model="loginEmail" type="email" class="form-control" placeholder="you@example.com" required>
            </div>
            <div class="mb-3">
              <label class="form-label small text-muted">Password</label>
              <input v-model="loginPassword" type="password" class="form-control" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2">Sign In</button>
          </form>

          <form v-if="view==='register'" @submit.prevent="handleRegister">
            <div class="mb-3">
              <label class="form-label small text-muted">Full Name</label>
              <input v-model="regName" type="text" class="form-control" placeholder="Jane Doe" required>
            </div>
            <div class="mb-3">
              <label class="form-label small text-muted">Email</label>
              <input v-model="regEmail" type="email" class="form-control" placeholder="you@example.com" required>
            </div>
            <div class="mb-3">
              <label class="form-label small text-muted">Password</label>
              <input v-model="regPassword" type="password" class="form-control" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn btn-success w-100 py-2">Create Account</button>
          </form>

          <div v-if="errorMsg" class="alert alert-danger mt-3 py-2 mb-0">{{ errorMsg }}</div>
          <div v-if="successMsg" class="alert alert-success mt-3 py-2 mb-0">{{ successMsg }}</div>
        </div>
      </div>
    </div>

    <!-- Logged-in dashboards -->
    <div v-else class="container-fluid mt-4 px-4">
      <AdminDashboard v-if="userRole === 'admin'" />
      <StaffDashboard v-else-if="userRole === 'staff'" />
      <TrekkerDashboard v-else />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from './api.js'
import AdminDashboard from './components/AdminDashboard.vue'
import StaffDashboard from './components/StaffDashboard.vue'
import TrekkerDashboard from './components/TrekkerDashboard.vue'

const view = ref('login')
const loggedIn = ref(false)
const userName = ref('')
const userRole = ref('')

const loginEmail = ref('')
const loginPassword = ref('')
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')

const errorMsg = ref('')
const successMsg = ref('')

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const data = await api.me()
      userName.value = data.name
      userRole.value = data.role
      loggedIn.value = true
    } catch {
      localStorage.removeItem('token')
    }
  }
})

function switchView(v) {
  view.value = v
  errorMsg.value = ''
  successMsg.value = ''
}

async function handleLogin() {
  errorMsg.value = ''
  try {
    const data = await api.login(loginEmail.value, loginPassword.value)
    localStorage.setItem('token', data.access_token)
    userName.value = data.name
    userRole.value = data.role
    loggedIn.value = true
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await api.register(regName.value, regEmail.value, regPassword.value)
    successMsg.value = 'Registered! You can now log in.'
    switchView('login')
  } catch (e) {
    errorMsg.value = e.message
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  loggedIn.value = false
  userName.value = ''
  userRole.value = ''
}
</script>