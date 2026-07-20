<template>
  <div ref="root" class="relative">
    <div class="relative">
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        ref="input"
        type="text"
        role="combobox"
        aria-autocomplete="list"
        :aria-expanded="open"
        :value="search"
        @input="onInput"
        @focus="onFocus"
        @keydown="onKeydown"
        :placeholder="placeholder"
        class="form-input pl-10 pr-9"
        autocomplete="off"
      />
      <button
        v-if="modelValue"
        type="button"
        @click="clear"
        aria-label="Effacer le club"
        class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-court-600 transition"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Dropdown -->
    <ul
      v-if="open"
      role="listbox"
      class="absolute z-30 mt-1 w-full max-h-72 overflow-auto rounded-lg border border-slate-200 bg-white shadow-lg py-1"
    >
      <li v-if="results.length === 0" class="px-3 py-2 text-sm text-slate-500">
        Aucun club trouvé
      </li>
      <li
        v-for="(club, i) in results"
        :key="club.slug"
        :ref="el => setOptionRef(el, i)"
        role="option"
        :aria-selected="club.slug === modelValue"
        @mousedown.prevent="select(club)"
        @mouseenter="highlighted = i"
        :class="[
          'px-3 py-2 text-sm cursor-pointer flex items-center justify-between gap-2',
          i === highlighted ? 'bg-court-50 text-court-800' : 'text-slate-700'
        ]"
      >
        <span class="truncate">{{ club.name }}</span>
        <svg v-if="club.slug === modelValue" class="w-4 h-4 flex-shrink-0 text-court-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import type { Club } from '../types'

const props = defineProps<{
  clubs: Club[]
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const root = ref<HTMLElement | null>(null)
const input = ref<HTMLInputElement | null>(null)
const search = ref('')
const open = ref(false)
const hasTyped = ref(false)
const highlighted = ref(0)
const optionEls: (HTMLElement | null)[] = []

function setOptionRef(el: any, i: number) {
  optionEls[i] = el as HTMLElement | null
}

const selectedClub = computed(() => props.clubs.find(c => c.slug === props.modelValue) || null)
const placeholder = computed(() => selectedClub.value ? selectedClub.value.name : 'Rechercher un club…')

function normalize(s: string): string {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
}

// Higher score = better match. Returns -1 for no match.
function score(query: string, text: string): number {
  const q = normalize(query)
  const t = normalize(text)
  if (!q) return 0

  const idx = t.indexOf(q)
  if (idx === 0) return 1000 - t.length
  if (idx > 0) {
    const boundary = !/[a-z0-9]/.test(t[idx - 1])
    return (boundary ? 800 : 500) - idx
  }

  // Subsequence: all query chars appear in order
  let ti = 0, qi = 0, start = -1
  while (ti < t.length && qi < q.length) {
    if (t[ti] === q[qi]) {
      if (start < 0) start = ti
      qi++
    }
    ti++
  }
  return qi === q.length ? 100 - start : -1
}

const results = computed<Club[]>(() => {
  if (!hasTyped.value || !search.value.trim()) {
    return props.clubs
  }
  const q = search.value.trim()
  return props.clubs
    .map(club => ({ club, s: score(q, club.name) }))
    .filter(x => x.s >= 0)
    .sort((a, b) => b.s - a.s || a.club.name.localeCompare(b.club.name))
    .map(x => x.club)
})

watch(results, () => { highlighted.value = 0; optionEls.length = 0 })

watch(highlighted, i => {
  nextTick(() => optionEls[i]?.scrollIntoView({ block: 'nearest' }))
})

// Keep the field in sync when the selection changes from outside (e.g. URL)
watch(() => props.modelValue, () => {
  if (!open.value) search.value = selectedClub.value?.name || ''
}, { immediate: true })

function onFocus() {
  open.value = true
  hasTyped.value = false
  nextTick(() => input.value?.select())
}

function onInput(e: Event) {
  search.value = (e.target as HTMLInputElement).value
  hasTyped.value = true
  open.value = true
}

function select(club: Club) {
  emit('update:modelValue', club.slug)
  search.value = club.name
  hasTyped.value = false
  open.value = false
  input.value?.blur()
}

function clear() {
  emit('update:modelValue', '')
  search.value = ''
  hasTyped.value = false
  nextTick(() => input.value?.focus())
}

function close() {
  open.value = false
  hasTyped.value = false
  search.value = selectedClub.value?.name || ''
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (!open.value) { open.value = true; return }
    highlighted.value = Math.min(highlighted.value + 1, results.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    highlighted.value = Math.max(highlighted.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const club = results.value[highlighted.value]
    if (club) select(club)
  } else if (e.key === 'Escape') {
    close()
    input.value?.blur()
  }
}

function onDocClick(e: MouseEvent) {
  if (root.value && !root.value.contains(e.target as Node)) close()
}

onMounted(() => document.addEventListener('mousedown', onDocClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>
