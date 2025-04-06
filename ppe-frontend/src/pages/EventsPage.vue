<!-- src/pages/EventsPage.vue -->
<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">События детекции</div>

    <div class="row q-col-gutter-md q-mb-md">
      <q-select
        v-model="selectedCamera"
        :options="cameraOptions"
        label="Камера"
        emit-value
        map-options
        @update:model-value="loadEvents"
      />
      <q-select
        v-model="selectedViolation"
        :options="violationOptions"
        label="Тип нарушения"
        @update:model-value="loadEvents"
      />
      <q-input
        v-model="startDate"
        label="От"
        type="date"
        @update:model-value="loadEvents"
      />
      <q-input
        v-model="endDate"
        label="До"
        type="date"
        @update:model-value="loadEvents"
      />
      <q-btn
        color="grey"
        label="Сбросить фильтры"
        icon="refresh"
        class="q-ml-sm"
        @click="resetFilters"
      />
      <q-btn
        color="secondary"
        label="Экспорт в Datumaro"
        icon="download"
        class="q-ml-md"
        @click="exportDatumaro"
      />
    </div>

    <q-table
      :columns="columns"
      :rows="events"
      row-key="id"
      title="Detection Events"
      v-model:pagination="pagination"
      dense
    >
      <template v-slot:body-cell-operations="{ row }">
        <q-td>
          <q-btn flat label="Детали" color="primary" @click="goDetail(row.id)" />
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const router = useRouter()

const events = ref([])
const columns = [
  { name: 'id', label: 'ID события', field: 'id', align: 'left' },
  { name: 'camera_id', label: 'ID камеры', field: 'camera_id', align: 'left' },
  { name: 'timestamp', label: 'Время', field: 'timestamp', align: 'left' },
  { name: 'image_url', label: 'Изображение', field: 'image_url', align: 'left' },
  { name: 'operations', label: 'Действия', align: 'center' }
]

const pagination = ref({
  page: 1,
  rowsPerPage: 10
})

const cameraOptions = ref([])
const selectedCamera = ref(null)

const violationOptions = [
  { label: 'Все', value: null },
  { label: 'No Helmet', value: 'no_helmet' },
  { label: 'No Vest', value: 'no_vest' },
  { label: 'No Helmet & No Vest', value: 'no_helmet_no_vest' },
  { label: 'None', value: 'none' }
]
const selectedViolation = ref(null)

const startDate = ref('')
const endDate = ref('')

async function loadCameras() {
  try {
    const resp = await axios.get('http://localhost:8000/api/v1/cameras/')
    cameraOptions.value = resp.data.map(cam => ({
      label: cam.name || `Камера #${cam.id}`,
      value: cam.id
    }))
  } catch (error) {
    console.error("Ошибка загрузки камер", error)
  }
}

async function loadEvents() {
  try {
    const params = {}
    if (selectedCamera.value) params.camera_id = selectedCamera.value
    if (selectedViolation.value) params.violation = selectedViolation.value
    if (startDate.value) params.start = startDate.value
    if (endDate.value) params.end = endDate.value

    const resp = await axios.get('http://localhost:8000/api/v1/detections/', { params })
    events.value = resp.data
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Ошибка загрузки событий' })
  }
}

function goDetail(eventId) {
  router.push(`/events/${eventId}`)
}

function resetFilters() {
  selectedCamera.value = null
  selectedViolation.value = null
  startDate.value = ''
  endDate.value = ''
  loadEvents()
}

async function exportDatumaro() {
  try {
    const params = {}
    if (selectedCamera.value) params.camera_id = selectedCamera.value
    if (startDate.value) params.start = startDate.value
    if (endDate.value) params.end = endDate.value

    const query = new URLSearchParams(params).toString()
    const url = `http://localhost:8000/api/v1/detections/export/datumaro?${query}`

    const link = document.createElement('a')
    link.href = url
    link.download = 'datumaro_export.zip'
    link.click()
    console.log("params:", params)
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Ошибка экспорта' })
  }
}

onMounted(() => {
  loadCameras()
  loadEvents()
})
</script>
