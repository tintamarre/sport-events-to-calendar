<template>
  <div v-if="events.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
    <span class="text-4xl">📅</span>
    <p class="mt-4 text-gray-600">Aucun match trouvé pour les critères sélectionnés</p>
  </div>

  <div v-else class="space-y-6">
    <div v-for="[date, dateEvents] in groupedEvents" :key="date" class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="bg-cpliege-blue text-white px-6 py-4">
        <h3 class="text-lg font-semibold">{{ formatDateHeader(date) }}</h3>
      </div>
      <div class="divide-y divide-gray-200">
        <EventCard
          v-for="(event, index) in dateEvents"
          :key="`${event.code}-${index}`"
          :event="event"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import EventCard from './EventCard.vue'
import { groupEventsByDate } from '../utils/filters'
import { parseDate, formatDate } from '../utils/dataLoader'
import type { CalendarEvent } from '../types'

const props = defineProps<{
  events: CalendarEvent[]
}>()

const groupedEvents = computed(() => {
  return Array.from(groupEventsByDate(props.events).entries())
})

function formatDateHeader(dateStr: string): string {
  const date = parseDate(dateStr)
  return date ? formatDate(date) : dateStr
}
</script>
