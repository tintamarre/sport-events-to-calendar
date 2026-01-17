<template>
  <div v-if="events.length === 0" class="text-center py-16 bg-white rounded-xl shadow-lg">
    <div class="text-6xl mb-4">📅</div>
    <h3 class="text-xl font-bold text-slate-700 mb-2">Aucun match trouvé</h3>
    <p class="text-slate-500">Essayez de modifier vos critères de recherche</p>
  </div>

  <div v-else class="space-y-5">
    <div v-for="[date, dateEvents] in groupedEvents" :key="date" class="bg-white rounded-xl shadow-lg overflow-hidden border border-slate-200 hover:shadow-xl transition-shadow">
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>📅</span>
          <span>{{ formatDateHeader(date) }}</span>
          <span class="ml-auto text-sm font-normal bg-white/20 px-3 py-1 rounded-full">
            {{ dateEvents.length }} match{{ dateEvents.length > 1 ? 's' : '' }}
          </span>
        </h3>
      </div>
      <div class="divide-y divide-slate-200">
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
