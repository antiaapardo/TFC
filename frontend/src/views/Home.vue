<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMainStore } from '../stores/main'
import { UI_MESSAGES } from '../constants/mercadillos'

import SearchBar from '../components/SearchBar.vue'
import EventoCard from '../components/EventoCard.vue'
import MapaInteractivo from '../components/MapaInteractivo.vue'

import { useRouter } from 'vue-router'

import '../css/Home.css'

const mainStore = useMainStore()
const router = useRouter()

const filtroTipo = ref('')
const filtroFecha = ref('')

onMounted(async () => {
  // Manejamos los errores si fallan las peticiones iniciales
  await mainStore.fetchCategorias()
  await mainStore.fetchEventos()
})

// Esta lógica computada es perfecta y reactiva
const eventosFiltrados = computed(() => {
  if (!mainStore.eventos) return []

  let lista = mainStore.eventos

  if (mainStore.verSoloFavoritos) {
    lista = lista.filter(e => 
      mainStore.favoritos.some(f => f.id_evento === e.id_evento)
    )
  }

  return lista.filter(e => {
    const cumpleTipo = !filtroTipo.value || e.id_categoria == filtroTipo.value
    const cumpleFecha = !filtroFecha.value || (e.fecha_inicio && e.fecha_inicio.includes(filtroFecha.value))
    
    return cumpleTipo && cumpleFecha
  })
})

const irADetalle = (id) => {
  router.push(`/evento/${id}`)
}
</script>

<template>
  <div class="home-container">
    <header class="home-header">
      <SearchBar 
        v-model:filtroTipo="filtroTipo" 
        v-model:filtroFecha="filtroFecha" 
        :categorias="mainStore.categorias" 
      />
    </header>

    <main class="main-layout">
      <div v-if="mainStore.isLoading" class="loading-state">
        {{ UI_MESSAGES.LOADING }}
      </div>

      <div v-else-if="mainStore.lastError" class="error-state">
        {{ UI_MESSAGES.ERROR_PREFIX }} {{ mainStore.lastError }}
      </div>

      <template v-else>
        <section class="events-grid">
          <EventoCard 
            v-for="item in eventosFiltrados" 
            :key="item.id_evento" 
            :evento="item" 
            @click="irADetalle(item.id_evento)"
          />
          
          <div v-if="eventosFiltrados.length === 0" class="empty-state">
            {{ mainStore.verSoloFavoritos ? 'Aún no tienes mercadillos guardados en favoritos.' : UI_MESSAGES.EMPTY }}
          </div>
        </section>

        <aside class="map-view">
          <MapaInteractivo :eventos="eventosFiltrados" />
        </aside>
      </template>
    </main>
  </div>
</template>