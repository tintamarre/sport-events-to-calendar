<template>
  <div class="min-h-screen flex flex-col bg-slate-100">
    <header class="bg-slate-900 sticky top-0 z-50 border-b-2 border-court-500">
      <div class="container mx-auto px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-court-500 flex items-center justify-center text-xl shadow-sm">
            🏀
          </div>
          <div class="leading-none">
            <h1 class="font-display font-semibold uppercase tracking-wide text-white text-xl md:text-2xl">
              CPLiège <span class="text-court-400">Basket</span>
            </h1>
            <p class="text-slate-400 text-xs mt-1">Calendrier des matchs · Province de Liège</p>
          </div>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-4 md:py-6 flex-1 w-full">
      <RouterView />
    </main>

    <footer class="bg-white border-t border-slate-200 mt-8">
      <div class="container mx-auto px-4 py-4 text-center">
        <p class="text-slate-500 text-xs">
          Données mises à jour automatiquement depuis
          <a href="http://www.cpliege.be" target="_blank" rel="noopener"
             class="text-court-600 hover:text-court-700 font-medium transition">cpliege.be</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>
