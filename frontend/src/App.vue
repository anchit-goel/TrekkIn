<template>
  <div>
    <!-- Fixed top nav shown when logged in -->
    <nav v-if="loggedIn" class="navbar navbar-dark navbar-brand-green px-3 top-navbar sticky-top">
      <span class="navbar-brand mb-0 fw-bold">TrekkIn</span>
      <div class="d-flex align-items-center flex-wrap gap-2">
        <span class="text-white-50">
          <span class="badge bg-light text-dark text-uppercase me-1">{{ userRole }}</span>
          {{ userName }}
        </span>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <!-- Auth screen -->
    <div v-if="!loggedIn" class="auth-wrapper">
      <div class="auth-card">
        <div class="card-header-custom">
          <h2 class="mb-1">TrekkIn</h2>
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

          <form v-if="view==='login'" @submit.prevent="handleLogin" novalidate>
            <div class="mb-3">
              <label class="form-label small text-muted">Email</label>
              <input
                v-model="loginEmail"
                type="email"
                class="form-control"
                :class="{ 'is-invalid': loginSubmitted && !validEmail(loginEmail) }"
                placeholder="Enter Email"
                @blur="loginTouched.email = true"
              >
              <div v-if="loginTouched.email && !validEmail(loginEmail)" class="text-danger small mt-1">Enter a valid email address.</div>
            </div>
            <div class="mb-3">
              <label class="form-label small text-muted">Password</label>
              <input
                v-model="loginPassword"
                type="password"
                class="form-control"
                :class="{ 'is-invalid': loginSubmitted && !loginPassword }"
                placeholder="Enter Password"
                @blur="loginTouched.password = true"
              >
              <div v-if="loginTouched.password && !loginPassword" class="text-danger small mt-1">Password is required.</div>
            </div>
            <button type="submit" class="btn btn-success w-100 py-2">Sign In</button>
          </form>

          <form v-if="view==='register'" @submit.prevent="handleRegister" novalidate>
            <div class="mb-3">
              <label class="form-label small text-muted">Full Name</label>
              <input
                v-model="regName"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': regSubmitted && !regName.trim() }"
                placeholder="Enter Name"
                @blur="regTouched.name = true"
              >
              <div v-if="regTouched.name && !regName.trim()" class="text-danger small mt-1">Name is required.</div>
            </div>
            <div class="mb-3">
              <label class="form-label small text-muted">Email</label>
              <input
                v-model="regEmail"
                type="email"
                class="form-control"
                :class="{ 'is-invalid': regSubmitted && !validEmail(regEmail) }"
                placeholder="Enter Email"
                @blur="regTouched.email = true"
              >
              <div v-if="regTouched.email && !validEmail(regEmail)" class="text-danger small mt-1">Enter a valid email address.</div>
            </div>
            <div class="mb-3">
              <label class="form-label small text-muted">Password</label>
              <input
                v-model="regPassword"
                type="password"
                class="form-control"
                :class="{ 'is-invalid': regSubmitted && regPassword.length < 6 }"
                placeholder="Enter Password"
                @blur="regTouched.password = true"
              >
              <div v-if="regTouched.password && regPassword.length < 6" class="text-danger small mt-1">Password must be at least 6 characters.</div>
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
    <ToastNotification ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from './api.js'
import AdminDashboard from './components/AdminDashboard.vue'
import StaffDashboard from './components/StaffDashboard.vue'
import TrekkerDashboard from './components/TrekkerDashboard.vue'
import { provide } from 'vue'
import ToastNotification from './components/ToastNotification.vue'

const toastRef = ref(null)
function showToast(message, type) {
  toastRef.value?.show(message, type)
}
provide('showToast', showToast)

const view = ref('login')
const loggedIn = ref(false)
const userName = ref('')
const userRole = ref('')

const loginEmail = ref('')
const loginPassword = ref('')
const loginSubmitted = ref(false)
const loginTouched = ref({ email: false, password: false })

const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regSubmitted = ref(false)
const regTouched = ref({ name: false, email: false, password: false })

const errorMsg = ref('')
const successMsg = ref('')

function validEmail(val) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)
}

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
  loginSubmitted.value = false
  loginTouched.value = { email: false, password: false }
  regSubmitted.value = false
  regTouched.value = { name: false, email: false, password: false }
}

async function handleLogin() {
  loginSubmitted.value = true
  loginTouched.value = { email: true, password: true }
  if (!validEmail(loginEmail.value) || !loginPassword.value) return
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
  regSubmitted.value = true
  regTouched.value = { name: true, email: true, password: true }
  if (!regName.value.trim() || !validEmail(regEmail.value) || regPassword.value.length < 6) return
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