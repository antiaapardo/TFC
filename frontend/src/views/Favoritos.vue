<script setup>
import { computed } from 'vue'
import { useMainStore } from '../stores/main'
import EventoCard from '../components/EventoCard.vue'
import { useRouter } from 'vue-router'

import '../css/Favoritos.css'
import '../css/Home.css' 

const mainStore = useMainStore()
const router = useRouter()

const irADetalle = (idEvento) => {
  router.push(`/evento/${idEvento}`)
}
const misFavoritos = computed(() => {
  if (!mainStore.eventos || !mainStore.favoritos) return []
  
  const idsFavoritos = mainStore.favoritos.map(f => f.id_evento)
  
  return mainStore.eventos.filter(evento => idsFavoritos.includes(evento.id_evento))
})
</script>

<template>
  <div class="favoritos-container">
    
    <div class="favoritos-header">
      <h1 class="favoritos-title">
        Mis Mercadillos Favoritos ❤️
      </h1>
      
      <router-link to="/" class="volver-link">
        ← Volver al inicio
      </router-link>
    </div>

    <div v-if="misFavoritos.length === 0" class="favoritos-empty-state">
      <h3>Aún no tienes mercadillos guardados.</h3>
      <p>Vuelve al inicio y pulsa el corazón en los mercadillos que más te gusten.</p>
    </div>

    <section v-else class="events-grid favoritos-grid">
      <EventoCard 
        v-for="evento in misFavoritos" 
        :key="evento.id_evento" 
        :evento="evento" 
        @click="irADetalle(evento.id_evento)" 
      />
    </section>
  </div>
</template>