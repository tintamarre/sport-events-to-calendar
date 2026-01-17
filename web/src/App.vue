<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
    <header class="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-xl sticky top-0 z-50">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center gap-3">
          <div class="text-4xl">🏀</div>
          <div>
            <h1 class="text-2xl md:text-3xl font-bold">CPLiège Basketball</h1>
            <p class="text-blue-100 text-sm hidden md:block">Calendrier Province de Liège</p>
          </div>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-6 md:py-8">
      <RouterView />
    </main>

    <footer class="bg-slate-800 text-white mt-12">
      <div class="container mx-auto px-4 py-6 text-center">
        <p class="text-slate-400 text-sm">
          Données mises à jour automatiquement depuis
          <a href="http://www.cpliege.be" target="_blank" class="text-blue-400 hover:text-blue-300 transition">cpliege.be</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>
