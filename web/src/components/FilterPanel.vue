<template>
  <div class="bg-white rounded-lg border border-neutral-200">
    <!-- Mobile toggle header -->
    <button
      @click="isExpanded = !isExpanded"
      class="w-full md:hidden flex items-center justify-between px-4 py-3 text-left"
    >
      <span class="font-medium text-neutral-800">Filtres</span>
      <svg
        :class="['w-5 h-5 text-neutral-500 transition-transform', isExpanded ? 'rotate-180' : '']"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Filter content -->
    <div :class="['md:block', isExpanded ? 'block' : 'hidden']">
      <div class="p-4 space-y-4 md:space-y-0">
        <!-- Main filters grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label class="form-label">Club</label>
            <select
              :value="selectedClub"
              @change="$emit('update:selectedClub', ($event.target as HTMLSelectElement).value)"
              class="form-select"
            >
              <option value="">Sélectionner un club</option>
              <option v-for="club in clubs" :key="club.slug" :value="club.slug">
                {{ club.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="form-label">Catégorie</label>
            <select
              :value="selectedCategory"
              @change="$emit('update:selectedCategory', ($event.target as HTMLSelectElement).value)"
              :disabled="!selectedClub"
              class="form-select disabled:bg-neutral-100 disabled:cursor-not-allowed disabled:text-neutral-400"
            >
              <option value="">Toutes les catégories</option>
              <option v-for="cat in currentCategories" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>

          <div>
            <label class="form-label">Date début</label>
            <input
              type="date"
              :value="dateFrom"
              @input="$emit('update:dateFrom', ($event.target as HTMLInputElement).value)"
              class="form-input"
            />
          </div>

          <div>
            <label class="form-label">Date fin</label>
            <input
              type="date"
              :value="dateTo"
              @input="$emit('update:dateTo', ($event.target as HTMLInputElement).value)"
              class="form-input"
            />
          </div>
        </div>

        <!-- Search and preset buttons -->
        <div class="flex flex-col md:flex-row gap-3 pt-4 border-t border-neutral-100 mt-4">
          <div class="flex-1">
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                :value="searchText"
                @input="$emit('update:searchText', ($event.target as HTMLInputElement).value)"
                placeholder="Rechercher une équipe..."
                class="form-input pl-10"
              />
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              @click="$emit('applyPreset', 'today')"
              class="btn btn-secondary text-sm"
            >
              Aujourd'hui
            </button>
            <button
              @click="$emit('applyPreset', 'week')"
              class="btn btn-secondary text-sm"
            >
              Cette semaine
            </button>
            <button
              @click="$emit('applyPreset', 'month')"
              class="btn btn-secondary text-sm"
            >
              Ce mois
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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

const isExpanded = ref(false)

const currentCategories = computed(() => {
  if (!props.selectedClub) return []
  const club = props.clubs.find(c => c.slug === props.selectedClub)
  return club?.categories || []
})
</script>
