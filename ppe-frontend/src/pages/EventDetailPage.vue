<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Детали события (ID: {{ eventId }})</div>

    <div v-if="eventData">
      <div><strong>ID камеры:</strong> {{ eventData.camera_id }}</div>
      <div><strong>Время:</strong> {{ eventData.timestamp }}</div>

      <!-- Обёртка с фиксированной высотой (можно по-другому) -->
      <div ref="stageContainer" style="border: 1px solid #ccc; display: inline-block;"></div>
    </div>
    <div v-else>Загрузка...</div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import axios from 'axios'
import Konva from 'konva'

const $q = useQuasar()
const route = useRoute()
const eventId = route.params.eventId

const eventData = ref(null)
const stageContainer = ref(null)

onMounted(async () => {
  try {
    const resp = await axios.get(`http://localhost:8000/api/v1/detections/${eventId}`)
    eventData.value = resp.data

    const img = new Image()
    img.crossOrigin = 'anonymous'
    const proxiedUrl = `http://localhost:8000/api/v1/proxy-image?url=${encodeURIComponent(eventData.value.image_url)}`
    img.src = proxiedUrl

    img.onload = async () => {
      const width = img.naturalWidth
      const height = img.naturalHeight

      // Ждём отрисовки DOM перед созданием Konva.Stage
      await nextTick()

      if (!stageContainer.value) {
        console.error('stageContainer не найден!')
        return
      }

      const stage = new Konva.Stage({
        container: stageContainer.value,
        width,
        height
      })

      const layer = new Konva.Layer()
      stage.add(layer)

      const konvaImage = new Konva.Image({
        image: img,
        width,
        height
      })
      layer.add(konvaImage)

      for (const person of eventData.value.persons) {
        const rectX = person.bbox_x * width
        const rectY = person.bbox_y * height
        const rectWidth = person.bbox_width * width
        const rectHeight = person.bbox_height * height

        // Прямоугольник
        layer.add(new Konva.Rect({
          x: rectX,
          y: rectY,
          width: rectWidth,
          height: rectHeight,
          stroke: 'red',
          strokeWidth: 2
        }))

        // Подпись (что нарушено)
        layer.add(new Konva.Text({
          x: rectX,
          y: rectY - 20, // чуть выше прямоугольника
          text: person.violation.replace(/_/g, ' '), // например: "no_helmet" → "no helmet"
          fontSize: 16,
          fontStyle: 'bold',
          fill: 'red',
          padding: 2
        }))
      }

      layer.draw()
    }
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Ошибка загрузки события' })
  }
})
</script>
