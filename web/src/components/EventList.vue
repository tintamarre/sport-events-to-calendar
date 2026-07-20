<template>
  <div v-if="events.length === 0" class="text-center py-14 card">
    <svg class="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
    <h3 class="text-lg font-medium text-slate-700 mb-1">Aucun match trouvé</h3>
    <p class="text-slate-500 text-sm">Modifiez la période ou la recherche pour voir d'autres matchs.</p>
  </div>

  <div v-else class="space-y-4">
    <div v-for="[date, dateEvents] in groupedEvents" :key="date" class="card overflow-hidden">
      <div
        :class="[
          'flex items-center justify-between px-4 py-2.5 border-b',
          isToday(date) ? 'bg-court-600 border-court-600' : 'bg-slate-50 border-slate-200'
        ]"
      >
        <h3 :class="['font-display uppercase tracking-wide text-sm', isToday(date) ? 'text-white' : 'text-slate-700']">
          {{ formatDateHeader(date) }}
          <span v-if="isToday(date)" class="ml-1.5 font-sans normal-case tracking-normal text-[11px] font-medium bg-white/25 px-1.5 py-0.5 rounded">
            Aujourd'hui
          </span>
        </h3>
        <span
          :class="[
            'text-xs tnum px-2 py-0.5 rounded-full',
            isToday(date) ? 'bg-white/20 text-white' : 'bg-white text-slate-500 border border-slate-200'
          ]"
        >
          {{ dateEvents.length }}
        </span>
      </div>
      <div class="divide-y divide-slate-100">
        <EventCard
          v-for="(event, index) in dateEvents"
          :key="`${event.code}-${index}`"
          :event="event"
          :clubName="clubName"
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
  clubName?: string
}>()

const groupedEvents = computed(() => {
  return Array.from(groupEventsByDate(props.events).entries())
})

function formatDateHeader(dateStr: string): string {
  const date = parseDate(dateStr)
  return date ? formatDate(date) : dateStr
}

function isToday(dateStr: string): boolean {
  const date = parseDate(dateStr)
  if (!date) return false
  const now = new Date()
  return date.getFullYear() === now.getFullYear()
    && date.getMonth() === now.getMonth()
    && date.getDate() === now.getDate()
}
</script>
