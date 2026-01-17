<template>
  <div class="px-6 py-4 hover:bg-gray-50 transition">
    <div class="flex flex-col sm:flex-row sm:items-center gap-4">
      <div class="flex-shrink-0">
        <div class="bg-cpliege-orange text-white px-4 py-2 rounded-lg text-center font-semibold">
          {{ event.time }}
        </div>
      </div>

      <div class="flex-1">
        <div class="flex items-center gap-3 text-lg font-semibold">
          <span class="text-gray-800">{{ event.team1 }}</span>
          <span class="text-gray-400">vs</span>
          <span class="text-gray-800">{{ event.team2 }}</span>
        </div>
        <div class="mt-2 flex flex-wrap gap-2 items-center text-sm">
          <span class="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-800 font-medium">
            {{ event.category }}
          </span>
          <span v-if="event.code" class="text-gray-500">
            Match #{{ event.code }}
          </span>
          <span v-if="event.other" class="text-gray-600">
            {{ event.other }}
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
