<template>
  <div class="card">
    <!-- Mobile toggle header -->
    <button
      @click="isExpanded = !isExpanded"
      class="w-full md:hidden flex items-center justify-between px-4 py-3 text-left"
    >
      <span class="font-medium text-slate-800">Filtres</span>
      <svg
        :class="['w-5 h-5 text-slate-500 transition-transform', isExpanded ? 'rotate-180' : '']"
        fill="none" viewBox="0 0 24 24" stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Filter content -->
    <div :class="['md:block', isExpanded ? 'block' : 'hidden']">
      <div class="p-4 space-y-4">
        <!-- Club + Category -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="form-label">Club</label>
            <ClubCombobox
              :clubs="clubs"
              :modelValue="selectedClub"
              @update:modelValue="$emit('update:selectedClub', $event)"
            />
          </div>

          <div>
            <label class="form-label">Catégorie</label>
            <select
              :value="selectedCategory"
              @change="$emit('update:selectedCategory', ($event.target as HTMLSelectElement).value)"
              :disabled="!selectedClub"
              class="form-select disabled:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400"
            >
              <option value="">Toutes les catégories</option>
              <option v-for="cat in currentCategories" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>
        </div>

        <!-- Search -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            :value="searchText"
            @input="$emit('update:searchText', ($event.target as HTMLInputElement).value)"
            placeholder="Rechercher une équipe, une salle…"
            class="form-input pl-10"
          />
        </div>

        <!-- Period: presets + custom range -->
        <div class="pt-3 border-t border-slate-100 space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-semibold uppercase tracking-wide text-slate-500 mr-1">Période</span>
            <button
              v-for="p in presets" :key="p.key"
              @click="choosePreset(p.key)"
              :class="['chip', activePreset === p.key ? 'chip-active' : 'chip-idle']"
            >
              {{ p.label }}
            </button>
            <button
              v-if="dateFrom || dateTo"
              @click="clearDates"
              class="ml-auto text-sm text-slate-500 hover:text-court-600 transition inline-flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Effacer
            </button>
          </div>

          <div class="flex flex-col sm:flex-row sm:items-center gap-2 text-sm">
            <label class="text-slate-500">Du</label>
            <input
              type="date"
              :value="dateFrom"
              @input="onDateInput('from', ($event.target as HTMLInputElement).value)"
              class="form-input sm:w-auto tnum"
            />
            <label class="text-slate-500 sm:ml-1">au</label>
            <input
              type="date"
              :value="dateTo"
              @input="onDateInput('to', ($event.target as HTMLInputElement).value)"
              class="form-input sm:w-auto tnum"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import ClubCombobox from './ClubCombobox.vue'
import type { Club } from '../types'

const props = defineProps<{
  clubs: Club[]
  selectedClub: string
  selectedCategory: string
  dateFrom: string
  dateTo: string
  searchText: string
}>()

const emit = defineEmits<{
  'update:selectedClub': [value: string]
  'update:selectedCategory': [value: string]
  'update:dateFrom': [value: string]
  'update:dateTo': [value: string]
  'update:searchText': [value: string]
  'applyPreset': [preset: 'today' | 'week' | 'month']
}>()

const presets = [
  { key: 'today', label: "Aujourd'hui" },
  { key: 'week', label: 'Cette semaine' },
  { key: 'month', label: 'Ce mois' },
] as const

const isExpanded = ref(false)
const activePreset = ref<'today' | 'week' | 'month' | ''>('')

const currentCategories = computed(() => {
  if (!props.selectedClub) return []
  const club = props.clubs.find(c => c.slug === props.selectedClub)
  return club?.categories || []
})

function choosePreset(key: 'today' | 'week' | 'month') {
  activePreset.value = key
  emit('applyPreset', key)
}

function onDateInput(which: 'from' | 'to', value: string) {
  activePreset.value = ''
  emit(which === 'from' ? 'update:dateFrom' : 'update:dateTo', value)
}

function clearDates() {
  activePreset.value = ''
  emit('update:dateFrom', '')
  emit('update:dateTo', '')
}

// Reset the highlighted preset if the dates get cleared elsewhere
watch(() => [props.dateFrom, props.dateTo], ([from, to]) => {
  if (!from && !to) activePreset.value = ''
})
</script>
