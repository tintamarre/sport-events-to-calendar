<template>
  <div class="px-6 py-5 hover:bg-slate-50 transition-colors border-l-4 border-transparent hover:border-blue-500">
    <div class="flex flex-col sm:flex-row sm:items-center gap-4">
      <div class="flex-shrink-0">
        <div class="bg-gradient-to-br from-orange-500 to-orange-600 text-white px-5 py-3 rounded-xl text-center font-bold shadow-md">
          <div class="text-lg">{{ event.time }}</div>
        </div>
      </div>

      <div class="flex-1">
        <div class="flex items-center gap-3 text-lg font-bold text-slate-800 mb-2">
          <span class="flex-1">{{ event.team1 }}</span>
          <span class="text-slate-400 text-sm font-normal">VS</span>
          <span class="flex-1 text-right">{{ event.team2 }}</span>
        </div>
        <div class="flex flex-wrap gap-2 items-center text-sm">
          <span class="inline-flex items-center px-3 py-1 rounded-lg bg-blue-100 text-blue-700 font-semibold">
            🏆 {{ event.category }}
          </span>
          <span v-if="event.code" class="inline-flex items-center px-3 py-1 rounded-lg bg-slate-100 text-slate-600 font-medium">
            #{{ event.code }}
          </span>
          <span v-if="event.other" class="inline-flex items-center px-3 py-1 rounded-lg bg-amber-100 text-amber-700">
            📍 {{ event.other }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CalendarEvent } from '../types'

defineProps<{
  event: CalendarEvent
}>()
</script>
