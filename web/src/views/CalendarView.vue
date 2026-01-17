<template>
  <div>
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="relative">
        <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        <div class="text-4xl absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">🏀</div>
      </div>
      <p class="mt-6 text-slate-600 font-medium">Chargement des matchs...</p>
    </div>

    <div v-else-if="error" class="max-w-2xl mx-auto">
      <div class="bg-red-50 border-l-4 border-red-500 rounded-lg p-6 shadow-lg">
        <div class="flex items-start">
          <div class="text-3xl mr-3">⚠️</div>
          <div>
            <h3 class="text-red-800 font-bold mb-1">Erreur de chargement</h3>
            <p class="text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else>
      <FilterPanel
        :clubs="manifest?.clubs || []"
        :selectedClub="selectedClub"
        :selectedCategory="selectedCategory"
        :dateFrom="dateFrom"
        :dateTo="dateTo"
        :searchText="searchText"
        @update:selectedClub="updateClub"
        @update:selectedCategory="updateCategory"
        @update:dateFrom="updateDateFrom"
        @update:dateTo="updateDateTo"
        @update:searchText="updateSearchText"
        @applyPreset="applyPreset"
      />

      <div v-if="selectedClub" class="mt-6">
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 class="text-3xl font-bold text-slate-800 mb-1">{{ clubName }}</h2>
              <p class="text-slate-500">
                <span class="inline-flex items-center gap-2">
                  <span class="text-2xl">📅</span>
                  <span class="font-semibold text-blue-600">{{ filteredEvents.length }}</span>
                  match{{ filteredEvents.length > 1 ? 's' : '' }} trouvé{{ filteredEvents.length > 1 ? 's' : '' }}
                </span>
              </p>
            </div>
            <div class="flex flex-wrap gap-2">
              <a
                v-if="csvUrl"
                :href="csvUrl"
                download
                class="px-4 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-all shadow-md hover:shadow-lg font-medium flex items-center gap-2"
              >
                <span>📥</span>
                <span>CSV</span>
              </a>
              <a
                v-if="icsUrl && selectedCategory"
                :href="icsUrl"
                download
                class="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all shadow-md hover:shadow-lg font-medium flex items-center gap-2"
              >
                <span>📅</span>
                <span>iCal</span>
              </a>
            </div>
          </div>
        </div>

        <EventList :events="filteredEvents" />
      </div>

      <div v-else class="text-center py-16 bg-white rounded-xl shadow-lg">
        <div class="text-7xl mb-4">🏀</div>
        <h3 class="text-2xl font-bold text-slate-700 mb-2">Choisissez votre club</h3>
        <p class="text-slate-500">Sélectionnez un club ci-dessus pour consulter le calendrier des matchs</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FilterPanel from '../components/FilterPanel.vue'
import EventList from '../components/EventList.vue'
import { loadManifest, loadAllClubEvents, getWeekRange } from '../utils/dataLoader'
import { filterEvents, sortEvents } from '../utils/filters'
import type { DataManifest, CalendarEvent, Club } from '../types'

const route = useRoute()
const router = useRouter()

const manifest = ref<DataManifest | null>(null)
const events = ref<CalendarEvent[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const selectedClub = ref<string>('')
const selectedCategory = ref<string>('')
const dateFrom = ref<string>('')
const dateTo = ref<string>('')
const searchText = ref<string>('')

const currentClub = computed(() => {
  if (!manifest.value || !selectedClub.value) return null
  return manifest.value.clubs.find(c => c.slug === selectedClub.value) || null
})

const clubName = computed(() => currentClub.value?.name || '')

const categories = computed(() => currentClub.value?.categories || [])

const csvUrl = computed(() => {
  if (!currentClub.value) return ''
  const base = import.meta.env.DEV ? '' : '/sport-events-to-calendar'
  return `${base}${currentClub.value.csvPath}`
})

const icsUrl = computed(() => {
  if (!currentClub.value || !selectedCategory.value) return ''
  const base = import.meta.env.DEV ? '' : '/sport-events-to-calendar'
  return `${base}${currentClub.value.icsFiles[selectedCategory.value]}`
})

const filteredEvents = computed(() => {
  const filtered = filterEvents(events.value, {
    category: selectedCategory.value || undefined,
    dateFrom: dateFrom.value || undefined,
    dateTo: dateTo.value || undefined,
    searchText: searchText.value || undefined
  })
  return sortEvents(filtered)
})

async function updateClub(clubSlug: string) {
  selectedClub.value = clubSlug
  selectedCategory.value = ''
  events.value = []

  if (clubSlug && currentClub.value) {
    try {
      loading.value = true
      events.value = await loadAllClubEvents(currentClub.value)
    } catch (e) {
      error.value = `Erreur lors du chargement des événements: ${e}`
    } finally {
      loading.value = false
    }
  }

  updateUrl()
}

function updateCategory(category: string) {
  selectedCategory.value = category
  updateUrl()
}

function updateDateFrom(date: string) {
  dateFrom.value = date
  updateUrl()
}

function updateDateTo(date: string) {
  dateTo.value = date
  updateUrl()
}

function updateSearchText(text: string) {
  searchText.value = text
  updateUrl()
}

function applyPreset(preset: 'today' | 'week' | 'month') {
  const now = new Date()
  now.setHours(0, 0, 0, 0)

  if (preset === 'today') {
    const today = now.toISOString().split('T')[0]
    dateFrom.value = today
    dateTo.value = today
  } else if (preset === 'week') {
    const { start, end } = getWeekRange(now)
    dateFrom.value = start.toISOString().split('T')[0]
    dateTo.value = end.toISOString().split('T')[0]
  } else if (preset === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    dateFrom.value = start.toISOString().split('T')[0]
    dateTo.value = end.toISOString().split('T')[0]
  }

  updateUrl()
}

function updateUrl() {
  const query: any = {}

  if (selectedClub.value) query.club = selectedClub.value
  if (selectedCategory.value) query.category = selectedCategory.value
  if (dateFrom.value) query.from = dateFrom.value
  if (dateTo.value) query.to = dateTo.value
  if (searchText.value) query.q = searchText.value

  router.replace({ query })
}

function loadFromUrl() {
  const query = route.query

  if (query.club && typeof query.club === 'string') {
    selectedClub.value = query.club
  }
  if (query.category && typeof query.category === 'string') {
    selectedCategory.value = query.category
  }
  if (query.from && typeof query.from === 'string') {
    dateFrom.value = query.from
  }
  if (query.to && typeof query.to === 'string') {
    dateTo.value = query.to
  }
  if (query.q && typeof query.q === 'string') {
    searchText.value = query.q
  }
}

onMounted(async () => {
  try {
    manifest.value = await loadManifest()
    loadFromUrl()

    if (selectedClub.value && currentClub.value) {
      events.value = await loadAllClubEvents(currentClub.value)
    }
  } catch (e) {
    error.value = `Erreur lors du chargement des données: ${e}`
  } finally {
    loading.value = false
  }
})

watch(() => route.query, () => {
  if (!loading.value) {
    loadFromUrl()
  }
})
</script>
