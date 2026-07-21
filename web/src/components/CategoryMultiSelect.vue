<template>
  <div ref="root" class="relative">
    <!-- Trigger -->
    <button
      type="button"
      :disabled="disabled"
      @click="toggle"
      class="form-select text-left flex items-center justify-between gap-2
             disabled:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400"
      :aria-expanded="open"
    >
      <span :class="modelValue.length ? 'text-slate-900' : 'text-slate-500'">
        {{ label }}
      </span>
    </button>

    <!-- Dropdown -->
    <div
      v-if="open"
      class="absolute z-30 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg"
    >
      <div class="p-2 border-b border-slate-100">
        <input
          ref="search"
          type="text"
          v-model="query"
          placeholder="Filtrer les catégories…"
          class="form-input text-sm py-1.5"
        />
      </div>
      <ul class="max-h-64 overflow-auto py-1">
        <li v-if="filtered.length === 0" class="px-3 py-2 text-sm text-slate-500">
          Aucune catégorie
        </li>
        <li
          v-for="cat in filtered"
          :key="cat"
          @click="toggleCat(cat)"
          class="px-3 py-2 text-sm cursor-pointer flex items-center gap-2 hover:bg-slate-50"
        >
          <span
            :class="[
              'w-4 h-4 rounded border flex items-center justify-center flex-shrink-0',
              modelValue.includes(cat) ? 'bg-court-600 border-court-600' : 'border-slate-300'
            ]"
          >
            <svg v-if="modelValue.includes(cat)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </span>
          <span class="text-slate-700 truncate">{{ cat }}</span>
        </li>
      </ul>
      <div v-if="modelValue.length" class="flex justify-end p-2 border-t border-slate-100">
        <button type="button" @click="clearAll" class="text-sm text-slate-500 hover:text-court-600 transition">
          Tout effacer
        </button>
      </div>
    </div>

    <!-- Selected chips -->
    <div v-if="modelValue.length" class="flex flex-wrap gap-1.5 mt-2">
      <span
        v-for="cat in modelValue"
        :key="cat"
        class="inline-flex items-center gap-1 pl-2 pr-1 py-0.5 rounded-full text-xs font-medium bg-court-50 text-court-700 border border-court-200"
      >
        {{ cat }}
        <button type="button" @click="toggleCat(cat)" :aria-label="`Retirer ${cat}`" class="hover:text-court-900">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps<{
  categories: string[]
  modelValue: string[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const root = ref<HTMLElement | null>(null)
const search = ref<HTMLInputElement | null>(null)
const open = ref(false)
const query = ref('')

const label = computed(() => {
  const n = props.modelValue.length
  if (n === 0) return 'Toutes les catégories'
  if (n === 1) return props.modelValue[0]
  return `${n} catégories`
})

function normalize(s: string): string {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
}

const filtered = computed(() => {
  const q = normalize(query.value.trim())
  if (!q) return props.categories
  return props.categories.filter(c => normalize(c).includes(q))
})

function toggle() {
  if (props.disabled) return
  open.value = !open.value
  if (open.value) nextTick(() => search.value?.focus())
}

function toggleCat(cat: string) {
  const set = new Set(props.modelValue)
  set.has(cat) ? set.delete(cat) : set.add(cat)
  emit('update:modelValue', [...set])
}

function clearAll() {
  emit('update:modelValue', [])
}

function onDocClick(e: MouseEvent) {
  if (root.value && !root.value.contains(e.target as Node)) {
    open.value = false
    query.value = ''
  }
}

onMounted(() => document.addEventListener('mousedown', onDocClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>
