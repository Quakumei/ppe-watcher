<!-- src/pages/DashboardPage.vue -->
<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Dashboard</div>
    <div class="row q-col-gutter-md">
      <q-card class="col">
        <q-card-section>
          <div class="text-h6">Камеры</div>
          <div class="text-subtitle1">{{ camerasCount }}</div>
        </q-card-section>
      </q-card>
      <q-card class="col">
        <q-card-section>
          <div class="text-h6">Нарушений сегодня</div>
          <div class="text-subtitle1">{{ eventsToday }}</div>
        </q-card-section>
      </q-card>
      <q-card class="col">
        <q-card-section>
          <div class="text-h6">Нарушений за все время</div>
          <div class="text-subtitle1">{{ eventsPeriod }}</div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
defineOptions({
  name: 'DashboardPage'
})
import { ref, onMounted } from 'vue'
import axios from 'axios'

const camerasCount = ref(0)
const eventsToday = ref(0)
const eventsPeriod = ref(0)

async function loadDashboardData() {
  // Здесь вы можете сделать запросы к API, чтобы получить статистику
  // Пример: получить список камер и установить camerasCount
  try {
    const cams = await axios.get('http://localhost:8000/api/v1/cameras')
    camerasCount.value = cams.data.length

    const events = await axios.get('http://localhost:8000/api/v1/detections')
    const now = new Date()
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)

    eventsToday.value = events.data.filter(e => {
      const eventDate = new Date(e.timestamp)
      return eventDate >= todayStart && eventDate < todayEnd
    }).length
    eventsPeriod.value = events.data.filter(e => true).length
  } catch (error) {
    console.error("Dashboard load error", error)
  }
}

onMounted(loadDashboardData)
onMounted(() => {
  console.log('Dashboard mounted')
  loadDashboardData()
})
</script>
