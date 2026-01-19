<template>
  <div v-if="events.length === 0" class="text-center py-12 bg-white rounded-lg border border-neutral-200">
    <svg class="w-12 h-12 mx-auto text-neutral-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
    <h3 class="text-lg font-medium text-neutral-700 mb-1">Aucun match trouvé</h3>
    <p class="text-neutral-500 text-sm">Essayez de modifier vos critères de recherche</p>
  </div>

  <div v-else class="space-y-4">
    <div v-for="[date, dateEvents] in groupedEvents" :key="date" class="bg-white rounded-lg border border-neutral-200 overflow-hidden">
      <div class="bg-neutral-50 border-b border-neutral-200 px-4 py-3 flex items-center justify-between">
        <h3 class="font-medium text-neutral-800">{{ formatDateHeader(date) }}</h3>
        <span class="text-xs text-neutral-500 bg-white px-2 py-1 rounded-full border border-neutral-200">
          {{ dateEvents.length }} match{{ dateEvents.length > 1 ? 's' : '' }}
        </span>
      </div>
      <div class="divide-y divide-neutral-100">
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
