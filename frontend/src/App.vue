<template>
<div class = "container mt-5" style = "max-width: 400px;">
  <h2 class = "mb-4">Trekking Management App - TrekkIn </h2>

  <div v-if = "!loggedIn">
    <div class="btn-group mb-3">
        <button class="btn btn-outline-primary" :class="{active: view==='login'}" @click="view='login'">Login</button>
        <button class="btn btn-outline-primary" :class="{active: view==='register'}" @click="view='register'">Register</button> 
    </div>

    <form v-if="view==='login'" @submit.prevent="handleLogin">
      <input v-model="loginEmail" type="email" class="form-control mb-2" placeholder="Email" required>
      <input v-model="loginPassword" type="password" class="form-control mb-2" placeholder="Password" required>
      <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>

    <form v-if="view==='register'" @submit.prevent="handleRegister">
      <input v-model="regName" type="text" class="form-control mb-2" placeholder="Full Name" required>
      <input v-model="regEmail" type="email" class="form-control mb-2" placeholder="Email" required>
      <input v-model="regPassword" type="password" class="form-control mb-2" placeholder="Password" required>
      <button type="submit" class="btn btn-success w-100">Register</button>
    </form>

    <p v-if="errorMsg" class="text-danger mt-2">{{ errorMsg }}</p>
    <p v-if="successMsg" class="text-success mt-2">{{ successMsg }}</p>

  </div>
  <div v-else>
    <p>Logged in as <strong>{{ userName }}</strong> ({{ userRole }})</p>
    <button class="btn btn-secondary" @click="handleLogout">Logout</button>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = 'http://127.0.0.1:5000/api'

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

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    fetchMe(token)
  }
})

async function fetchMe(token) {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) {
    const data = await res.json()
    userName.value = data.name
    userRole.value = data.role
    loggedIn.value = true
  } else {
    localStorage.removeItem('token')
  }
}

async function handleLogin() {
  errorMsg.value = ''
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: loginEmail.value, password: loginPassword.value })
  })
  const data = await res.json()
  if (res.ok) {
    localStorage.setItem('token', data.access_token)
    userName.value = data.name
    userRole.value = data.role
    loggedIn.value = true
  } else {
    errorMsg.value = data.error || 'Login failed'
  }
}

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: regName.value, email: regEmail.value, password: regPassword.value })
  })
  const data = await res.json()
  if (res.ok) {
    successMsg.value = 'Registered! You can now log in.'
    view.value = 'login'
  } else {
    errorMsg.value = data.error || 'Registration failed'
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  loggedIn.value = false
  userName.value = ''
  userRole.value = ''
}
</script>

