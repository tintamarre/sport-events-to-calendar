<template>
  <div class="bg-white rounded-lg shadow-lg p-6 space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Club</label>
        <select
          :value="selectedClub"
          @change="$emit('update:selectedClub', ($event.target as HTMLSelectElement).value)"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cpliege-blue focus:border-transparent"
        >
          <option value="">-- Sélectionner un club --</option>
          <option v-for="club in clubs" :key="club.slug" :value="club.slug">
            {{ club.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
        <select
          :value="selectedCategory"
          @change="$emit('update:selectedCategory', ($event.target as HTMLSelectElement).value)"
          :disabled="!selectedClub"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cpliege-blue focus:border-transparent disabled:bg-gray-100"
        >
          <option value="">-- Toutes les catégories --</option>
          <option v-for="cat in currentCategories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Date début</label>
        <input
          type="date"
          :value="dateFrom"
          @input="$emit('update:dateFrom', ($event.target as HTMLInputElement).value)"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cpliege-blue focus:border-transparent"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Date fin</label>
        <input
          type="date"
          :value="dateTo"
          @input="$emit('update:dateTo', ($event.target as HTMLInputElement).value)"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cpliege-blue focus:border-transparent"
        />
      </div>
    </div>

    <div class="flex flex-wrap gap-3 items-center">
      <div class="flex-1 min-w-[200px]">
        <input
          type="text"
          :value="searchText"
          @input="$emit('update:searchText', ($event.target as HTMLInputElement).value)"
          placeholder="Rechercher une équipe..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cpliege-blue focus:border-transparent"
        />
      </div>

      <div class="flex gap-2">
        <button
          @click="$emit('applyPreset', 'today')"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
        >
          Aujourd'hui
        </button>
        <button
          @click="$emit('applyPreset', 'week')"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
        >
          Cette semaine
        </button>
        <button
          @click="$emit('applyPreset', 'month')"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
        >
          Ce mois
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Club } from '../types'

const props = defineProps<{
  clubs: Club[]
  selectedClub: string
  selectedCategory: string
  dateFrom: string
  dateTo: string
  searchText: string
}>()

defineEmits<{
  'update:selectedClub': [value: string]
  'update:selectedCategory': [value: string]
  'update:dateFrom': [value: string]
  'update:dateTo': [value: string]
  'update:searchText': [value: string]
  'applyPreset': [preset: 'today' | 'week' | 'month']
}>()

const currentCategories = computed(() => {
  if (!props.selectedClub) return []
  const club = props.clubs.find(c => c.slug === props.selectedClub)
  return club?.categories || []
})
</script>
