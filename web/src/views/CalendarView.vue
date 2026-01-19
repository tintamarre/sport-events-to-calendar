<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="w-10 h-10 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
      <p class="mt-4 text-neutral-500 text-sm">Chargement des matchs...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="max-w-lg mx-auto">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex items-start gap-3">
          <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-red-800 font-medium text-sm">Erreur de chargement</h3>
            <p class="text-red-700 text-sm mt-1">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main content -->
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

      <!-- Club selected -->
      <div v-if="selectedClub" class="mt-4">
        <!-- Club header -->
        <div class="bg-white rounded-lg border border-neutral-200 p-4 mb-4">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 class="text-xl font-semibold text-neutral-800">{{ clubName }}</h2>
              <p class="text-neutral-500 text-sm mt-0.5">
                <span class="font-medium text-indigo-600">{{ filteredEvents.length }}</span>
                match{{ filteredEvents.length > 1 ? 's' : '' }} trouvé{{ filteredEvents.length > 1 ? 's' : '' }}
              </p>
            </div>
            <div class="flex flex-wrap gap-2">
              <a
                v-if="csvUrl"
                :href="csvUrl"
                download
                class="btn btn-secondary text-sm flex items-center gap-1.5"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                CSV
              </a>
              <button
                v-if="events.length > 0"
                @click="handleICSDownload"
                class="btn btn-primary text-sm flex items-center gap-1.5"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                iCal
              </button>
            </div>
          </div>
        </div>

        <EventList :events="filteredEvents" />
      </div>

      <!-- No club selected -->
      <div v-else class="text-center py-12 bg-white rounded-lg border border-neutral-200 mt-4">
        <div class="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="text-3xl">🏀</span>
        </div>
        <h3 class="text-lg font-medium text-neutral-700 mb-1">Choisissez votre club</h3>
        <p class="text-neutral-500 text-sm">Sélectionnez un club ci-dessus pour consulter le calendrier des matchs</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FilterPanel from '../components/FilterPanel.vue'
import EventList from '../components/EventList.vue'
import { loadManifest, loadClubJSON, getWeekRange, downloadICS } from '../utils/dataLoader'
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

function handleICSDownload() {
  if (!currentClub.value) return

  const eventsToDownload = selectedCategory.value
    ? filteredEvents.value
    : events.value

  const calName = selectedCategory.value
    ? `${clubName.value} - ${selectedCategory.value}`
    : clubName.value

  const filename = selectedCategory.value
    ? `${currentClub.value.slug}-${selectedCategory.value.toLowerCase().replace(/\s+/g, '-')}.ics`
    : `${currentClub.value.slug}.ics`

  downloadICS(eventsToDownload, calName, filename)
}

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
      events.value = await loadClubJSON(currentClub.value)
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
      events.value = await loadClubJSON(currentClub.value)
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
