<template>
  <div class="min-h-screen bg-neutral-50">
    <header class="bg-white border-b border-neutral-200 sticky top-0 z-50">
      <div class="container mx-auto px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
            <span class="text-xl">🏀</span>
          </div>
          <div>
            <h1 class="text-lg md:text-xl font-semibold text-neutral-800">CPLiège Basketball</h1>
            <p class="text-neutral-500 text-xs hidden md:block">Calendrier Province de Liège</p>
          </div>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-4 md:py-6">
      <RouterView />
    </main>

    <footer class="bg-white border-t border-neutral-200 mt-8">
      <div class="container mx-auto px-4 py-4 text-center">
        <p class="text-neutral-500 text-xs">
          Données mises à jour automatiquement depuis
          <a href="http://www.cpliege.be" target="_blank" class="text-indigo-600 hover:text-indigo-500 transition">cpliege.be</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>
