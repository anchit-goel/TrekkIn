<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100;">
    <div v-for="t in toasts" :key="t.id"
         class="toast show mb-2"
         :class="t.type === 'error' ? 'text-bg-danger' : 'text-bg-success'">
      <div class="d-flex">
        <div class="toast-body">{{ t.message }}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="remove(t.id)"></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let idCounter = 0

function show(message, type = 'success') {
  const id = idCounter++
  toasts.value.push({ id, message, type })
  setTimeout(() => remove(id), 3500)
}

function remove(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

defineExpose({ show })
</script>