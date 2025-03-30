<!-- src/pages/CamerasPage.vue -->
<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Список камер</div>
    <q-table
      :columns="columns"
      :rows="cameraList"
      row-key="id"
      grid
      title="Cameras"
    >
      <template v-slot:top-right>
        <q-btn color="primary" label="Добавить камеру" @click="onAddCamera" />
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

const $q = useQuasar()
const cameraList = ref([])

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'name', label: 'Название', field: 'name', align: 'left' },
  { name: 'rtsp_url', label: 'RTSP URL', field: 'rtsp_url', align: 'left' },
  { name: 'location', label: 'Местоположение', field: 'location', align: 'left' },
  { name: 'is_active', label: 'Активна', field: 'is_active', align: 'center' }
]

async function loadCameras() {
  try {
    const resp = await axios.get('http://localhost:8000/api/v1/cameras/')
    cameraList.value = resp.data
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Не удалось загрузить камеры' })
  }
}

function onAddCamera() {
  axios.post('http://localhost:8000/api/v1/cameras', {
    name: 'Новая камера',
    rtsp_url: 'rtsp://example',
    location: 'Новая локация',
    is_active: true
  }).then(() => {
    $q.notify({ type: 'positive', message: 'Камера добавлена' })
    loadCameras()
  }).catch(() => {
    $q.notify({ type: 'negative', message: 'Ошибка при добавлении камеры' })
  })
}

onMounted(loadCameras)
</script>
