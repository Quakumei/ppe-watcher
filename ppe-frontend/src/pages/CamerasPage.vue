<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Список камер</div>

    <q-btn
      color="negative"
      label="Удалить выбранные"
      :disable="selectedCameraIds.length === 0"
      class="q-mb-md"
      @click="confirmDeleteDialog = true"
    />

    <q-table
      :columns="columns"
      :rows="cameraList"
      row-key="id"
      selection="multiple"
      v-model:selected="selectedCameras"
      title="Камеры"
    >
      <template v-slot:top-right>
        <q-btn color="primary" label="Добавить камеру" @click="addCameraDialog = true" />
      </template>
    </q-table>

    <!-- Диалог удаления -->
    <q-dialog v-model="confirmDeleteDialog" persistent>
      <q-card>
        <q-card-section class="text-h6">Подтверждение удаления</q-card-section>
        <q-card-section>
          Вы уверены, что хотите удалить {{ selectedCameraIds.length }}
          {{ selectedCameraIds.length === 1 ? 'камеру' : 'камеры' }}?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Отмена" v-close-popup />
          <q-btn color="negative" label="Удалить" @click="deleteSelectedCameras" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Диалог добавления -->
    <q-dialog v-model="addCameraDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="text-h6">Добавить камеру</q-card-section>
        <q-card-section>
          <q-input v-model="newCamera.name" label="Название" />
          <q-input v-model="newCamera.rtsp_url" label="RTSP URL" class="q-mt-sm" />
          <q-input v-model="newCamera.location" label="Местоположение" class="q-mt-sm" />
          <q-toggle v-model="newCamera.is_active" label="Активна" class="q-mt-md" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Отмена" v-close-popup />
          <q-btn color="primary" label="Добавить" @click="submitNewCamera" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Notify } from 'quasar'
import axios from 'axios'

const cameraList = ref([])
const selectedCameras = ref([])
const confirmDeleteDialog = ref(false)
const addCameraDialog = ref(false)

const newCamera = ref({
  name: '',
  rtsp_url: '',
  location: '',
  is_active: true
})

const selectedCameraIds = computed(() => selectedCameras.value.map(cam => cam.id))

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
    Notify.create({ type: 'negative', message: 'Не удалось загрузить камеры' })
  }
}

async function deleteSelectedCameras() {
  const idsToDelete = selectedCameraIds.value
  for (const id of idsToDelete) {
    try {
      await axios.delete(`http://localhost:8000/api/v1/cameras/${id}`)
    } catch (error) {
      Notify.create({ type: 'negative', message: `Ошибка при удалении камеры ID ${id}` })
    }
  }

  Notify.create({ type: 'positive', message: `Удалено ${idsToDelete.length} камер` })
  selectedCameras.value = []
  confirmDeleteDialog.value = false
  loadCameras()
}

async function submitNewCamera() {
  try {
    await axios.post('http://localhost:8000/api/v1/cameras', newCamera.value)
    Notify.create({ type: 'positive', message: 'Камера добавлена' })
    addCameraDialog.value = false
    newCamera.value = {
      name: '',
      rtsp_url: '',
      location: '',
      is_active: true
    }
    loadCameras()
  } catch (e) {
    Notify.create({ type: 'negative', message: 'Ошибка при добавлении камеры' })
  }
}

onMounted(loadCameras)
</script>
