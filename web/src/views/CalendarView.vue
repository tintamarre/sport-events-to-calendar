<template>
  <div>
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-cpliege-blue"></div>
      <p class="mt-4 text-gray-600">Chargement des données...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <p class="text-red-800">{{ error }}</p>
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

      <div v-if="selectedClub" class="mt-8">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-2xl font-bold">{{ clubName }}</h2>
            <p class="text-gray-600">{{ filteredEvents.length }} match(s) trouvé(s)</p>
          </div>
          <div class="flex gap-2">
            <a
              v-if="csvUrl"
              :href="csvUrl"
              download
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              Télécharger CSV
            </a>
            <a
              v-if="icsUrl && selectedCategory"
              :href="icsUrl"
              download
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Télécharger ICS
            </a>
          </div>
        </div>

        <EventList :events="filteredEvents" />
      </div>

      <div v-else class="text-center py-12 bg-white rounded-lg shadow">
        <span class="text-6xl">🏀</span>
        <h3 class="text-xl font-semibold mt-4 text-gray-700">Sélectionnez un club</h3>
        <p class="text-gray-500 mt-2">Choisissez un club dans le menu ci-dessus pour voir les matchs</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FilterPanel from '../components/FilterPanel.vue'
import EventList from '../components/EventList.vue'
import { loadManifest, loadClubEvents, getWeekRange } from '../utils/dataLoader'
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
      events.value = await loadClubEvents(currentClub.value.csvPath)
    } catch (e) {
      error.value = `Erreur lors du chargement des événements: ${e}`
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
      events.value = await loadClubEvents(currentClub.value.csvPath)
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
