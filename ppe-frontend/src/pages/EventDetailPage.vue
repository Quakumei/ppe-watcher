<!-- src/pages/EventDetailPage.vue -->
<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Детали события (ID: {{ eventId }})</div>

    <div v-if="eventData">
      <div><strong>ID камеры:</strong> {{ eventData.camera_id }}</div>
      <div><strong>Время:</strong> {{ eventData.timestamp }}</div>
      <q-img
        :src="eventData.image_url"
        style="width: 600px; height: auto;"
      />
      <div class="q-mt-md">
        <div v-for="(person, index) in eventData.persons" :key="index">
          <div>
            <strong>Нарушение:</strong> {{ person.violation }}
            (x={{ person.bbox_x }}, y={{ person.bbox_y }}, w={{ person.bbox_width }}, h={{ person.bbox_height }})
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      Загрузка...
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const route = useRoute()
const eventId = route.params.eventId

const eventData = ref(null)

async function loadEvent() {
  try {
    const resp = await axios.get(`http://localhost:8000/api/v1/detections/${eventId}`)
    eventData.value = resp.data
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Ошибка загрузки события' })
  }
}

onMounted(loadEvent)
</script>
