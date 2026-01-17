<template>
  <div class="min-h-screen">
    <header class="bg-cpliege-blue text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center gap-4">
          <span class="text-4xl">🏀</span>
          <div>
            <h1 class="text-3xl font-bold">Calendrier CPLiège</h1>
            <p class="text-blue-200">Basketball - Province de Liège</p>
          </div>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <RouterView />
    </main>

    <footer class="bg-gray-800 text-white mt-12">
      <div class="container mx-auto px-4 py-6 text-center">
        <p class="text-gray-400">
          Données automatiquement mises à jour depuis
          <a href="http://www.cpliege.be" target="_blank" class="text-cpliege-orange hover:underline">cpliege.be</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>
