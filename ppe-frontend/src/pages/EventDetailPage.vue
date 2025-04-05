<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Детали события (ID: {{ eventId }})</div>

    <div v-if="eventData">
      <div><strong>ID камеры:</strong> {{ eventData.camera_id }}</div>
      <div><strong>Время:</strong> {{ eventData.timestamp }}</div>

      <div style="width: 800px; height: auto;" class="q-mt-md">
        <v-stage :config="{ width: stageWidth, height: stageHeight }">
          <v-layer>
            <v-image :image="imageObj" />
            <v-rect
              v-for="(person, index) in eventData.persons"
              :key="index"
              :config="getBBoxConfig(person)"
            />
          </v-layer>
        </v-stage>
      </div>
    </div>

    <div v-else>Загрузка...</div>
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
const imageObj = ref(null)
const stageWidth = 800
const stageHeight = 600

async function loadEvent() {
  try {
    const resp = await axios.get(`http://localhost:8000/api/v1/detections/${eventId}`)
    eventData.value = resp.data

    const img = new window.Image()
    img.src = eventData.value.image_url
    img.onload = () => {
      imageObj.value = img
    }
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Ошибка загрузки события' })
  }
}

function getBBoxConfig(person) {
  return {
    x: person.bbox_x * stageWidth,
    y: person.bbox_y * stageHeight,
    width: person.bbox_width * stageWidth,
    height: person.bbox_height * stageHeight,
    stroke: 'red',
    strokeWidth: 2
  }
}

onMounted(loadEvent)
</script>
