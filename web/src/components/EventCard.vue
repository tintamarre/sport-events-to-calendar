<template>
  <div class="px-4 py-3 hover:bg-neutral-50 transition-colors">
    <div class="flex flex-col sm:flex-row sm:items-center gap-3">
      <!-- Time badge -->
      <div class="flex-shrink-0">
        <div class="inline-flex items-center px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg font-semibold text-sm">
          {{ event.time }}
        </div>
      </div>

      <!-- Match info -->
      <div class="flex-1 min-w-0">
        <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 text-sm">
          <span class="font-medium text-neutral-800 truncate">{{ event.team1 }}</span>
          <span class="text-neutral-400 text-xs hidden sm:inline">vs</span>
          <span class="font-medium text-neutral-800 truncate">{{ event.team2 }}</span>
        </div>

        <!-- Tags -->
        <div class="flex flex-wrap gap-1.5 mt-2">
          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-neutral-100 text-neutral-600">
            {{ event.category }}
          </span>
          <span v-if="event.code" class="inline-flex items-center px-2 py-0.5 rounded text-xs text-neutral-400">
            #{{ event.code }}
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
