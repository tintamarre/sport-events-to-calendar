<template>
  <div class="px-4 py-3 hover:bg-slate-50 transition-colors">
    <div class="flex gap-3 sm:gap-4">
      <!-- Time chip -->
      <div class="flex-shrink-0">
        <div class="inline-flex items-center justify-center min-w-[3.5rem] px-2.5 py-1.5 rounded-lg
                    bg-court-50 text-court-700 font-display font-semibold text-base tnum">
          {{ event.time }}
        </div>
      </div>

      <!-- Match -->
      <div class="flex-1 min-w-0">
        <!-- Teams -->
        <div class="space-y-0.5">
          <div class="flex items-center gap-2">
            <span :class="['w-1.5 h-1.5 rounded-full flex-shrink-0', isOurs(event.team1) ? 'bg-court-500' : 'bg-transparent']"></span>
            <span :class="['truncate', isOurs(event.team1) ? 'font-semibold text-slate-900' : 'text-slate-700']">
              {{ event.team1 }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span :class="['w-1.5 h-1.5 rounded-full flex-shrink-0', isOurs(event.team2) ? 'bg-court-500' : 'bg-transparent']"></span>
            <span :class="['truncate', isOurs(event.team2) ? 'font-semibold text-slate-900' : 'text-slate-700']">
              {{ event.team2 }}
            </span>
          </div>
        </div>

        <!-- Meta: category · venue · code -->
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-slate-500">
          <span class="inline-flex items-center px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
            {{ event.category }}
          </span>
          <span v-if="venue" class="inline-flex items-center gap-1 min-w-0">
            <svg class="w-3.5 h-3.5 flex-shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="truncate">{{ venue }}</span>
          </span>
          <span v-if="event.code" class="text-slate-400 tnum">#{{ event.code }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CalendarEvent } from '../types'

const props = defineProps<{
  event: CalendarEvent
  clubName?: string
}>()

// The "salle" lives in `other` (e.g. "(Salle de Grivegnée)"); fall back to location.
const venue = computed(() => {
  const raw = (props.event.other || props.event.location || '').trim()
  return raw.replace(/^\(+|\)+$/g, '').trim()
})

// Strip the numeric id prefix and normalise, so we can flag the user's own team.
const clubCore = computed(() => {
  return (props.clubName || '')
    .replace(/^\d+\s*/, '')
    .toLowerCase()
    .trim()
})

function isOurs(team: string): boolean {
  const core = clubCore.value
  if (core.length < 3) return false
  return team.toLowerCase().includes(core)
}
</script>
