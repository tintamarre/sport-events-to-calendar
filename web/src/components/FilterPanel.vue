<template>
  <div class="bg-white rounded-xl shadow-xl p-6 space-y-6 border border-slate-200">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
          <span>🏀</span>
          <span>Club</span>
        </label>
        <select
          :value="selectedClub"
          @change="$emit('update:selectedClub', ($event.target as HTMLSelectElement).value)"
          class="w-full px-4 py-2.5 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white font-medium"
        >
          <option value="">-- Sélectionner un club --</option>
          <option v-for="club in clubs" :key="club.slug" :value="club.slug">
            {{ club.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
          <span>📂</span>
          <span>Catégorie</span>
        </label>
        <select
          :value="selectedCategory"
          @change="$emit('update:selectedCategory', ($event.target as HTMLSelectElement).value)"
          :disabled="!selectedClub"
          class="w-full px-4 py-2.5 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:cursor-not-allowed transition-all bg-white font-medium"
        >
          <option value="">-- Toutes les catégories --</option>
          <option v-for="cat in currentCategories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
          <span>📅</span>
          <span>Date début</span>
        </label>
        <input
          type="date"
          :value="dateFrom"
          @input="$emit('update:dateFrom', ($event.target as HTMLInputElement).value)"
          class="w-full px-4 py-2.5 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white font-medium"
        />
      </div>

      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
          <span>📅</span>
          <span>Date fin</span>
        </label>
        <input
          type="date"
          :value="dateTo"
          @input="$emit('update:dateTo', ($event.target as HTMLInputElement).value)"
          class="w-full px-4 py-2.5 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white font-medium"
        />
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-3 items-stretch md:items-center border-t pt-4">
      <div class="flex-1 min-w-[200px]">
        <div class="relative">
          <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 text-xl">🔍</span>
          <input
            type="text"
            :value="searchText"
            @input="$emit('update:searchText', ($event.target as HTMLInputElement).value)"
            placeholder="Rechercher une équipe..."
            class="w-full pl-11 pr-4 py-2.5 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white font-medium"
          />
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          @click="$emit('applyPreset', 'today')"
          class="px-4 py-2.5 bg-slate-100 hover:bg-blue-100 text-slate-700 hover:text-blue-700 rounded-lg transition-all font-medium shadow-sm hover:shadow border border-slate-200"
        >
          📆 Aujourd'hui
        </button>
        <button
          @click="$emit('applyPreset', 'week')"
          class="px-4 py-2.5 bg-slate-100 hover:bg-blue-100 text-slate-700 hover:text-blue-700 rounded-lg transition-all font-medium shadow-sm hover:shadow border border-slate-200"
        >
          📅 Cette semaine
        </button>
        <button
          @click="$emit('applyPreset', 'month')"
          class="px-4 py-2.5 bg-slate-100 hover:bg-blue-100 text-slate-700 hover:text-blue-700 rounded-lg transition-all font-medium shadow-sm hover:shadow border border-slate-200"
        >
          🗓️ Ce mois
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
