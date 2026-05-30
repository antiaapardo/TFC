<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMainStore } from '../stores/main'
import { UI_MESSAGES } from '../constants/mercadillos'

import SearchBar from '../components/SearchBar.vue'
import EventoCard from '../components/EventoCard.vue'
import MapaInteractivo from '../components/MapaInteractivo.vue'
import FooterMEC from '../components/FooterMEC.vue';

import { useRouter } from 'vue-router'

import '../css/Home.css'

const mainStore = useMainStore()
const router = useRouter()

const filtroTipo = ref('')
const filtroFechaInicio = ref('')
const filtroFechaFin = ref('')

const usandoCercania = ref(false)
const userLat = ref(null)
const userLon = ref(null)
const radioMaximoKm = ref(10)

onMounted(async () => {
  if (mainStore.categorias.length === 0) {
    await mainStore.fetchCategorias()
  }  
  await mainStore.fetchEventos()
})

const conmutarFiltroCercania = () => {
  if (usandoCercania.value) {
    usandoCercania.value = false
    return
  }

  if (!navigator.geolocation) {
    alert('Tu navegador no soporta geolocalización.')
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      userLat.value = position.coords.latitude
      userLon.value = position.coords.longitude
      usandoCercania.value = true
    },
    (error) => {
      console.error('Error al obtener ubicación:', error)
      alert('No se pudo acceder a tu ubicación. Asegúrate de dar permisos en el navegador.')
    }
  );
}

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
    
    let cumpleFecha = true
    
    if (e.fecha_inicio) {
      const fechaEvento = new Date(e.fecha_inicio)
      fechaEvento.setHours(0, 0, 0, 0)

      if (filtroFechaInicio.value && !filtroFechaFin.value) {
        const fechaInicio = new Date(filtroFechaInicio.value)
        fechaInicio.setHours(0, 0, 0, 0)
        if (fechaEvento.getTime() !== fechaInicio.getTime()) cumpleFecha = false
      } 
      else if (filtroFechaInicio.value && filtroFechaFin.value) {
        const fechaInicio = new Date(filtroFechaInicio.value)
        fechaInicio.setHours(0, 0, 0, 0)
        const fechaFin = new Date(filtroFechaFin.value)
        fechaFin.setHours(0, 0, 0, 0)
        if (fechaEvento < fechaInicio || fechaEvento > fechaFin) cumpleFecha = false
      }
      else if (!filtroFechaInicio.value && filtroFechaFin.value) {
        const fechaFin = new Date(filtroFechaFin.value)
        fechaFin.setHours(0, 0, 0, 0)
        if (fechaEvento > fechaFin) cumpleFecha = false
      }
    } else if (filtroFechaInicio.value || filtroFechaFin.value) {
      cumpleFecha = false
    }
    
    let cumpleCercania = true
    if (usandoCercania.value && userLat.value && userLon.value) {
      const distancia = calcularDistanciaEnKm(userLat.value, userLon.value, e.latitud, e.longitud)
      cumpleCercania = distancia <= radioMaximoKm.value
    }
    
    return cumpleTipo && cumpleFecha && cumpleCercania
  })
})

const irADetalle = (id) => {
  router.push(`/evento/${id}`)
}

const calcularDistanciaEnKm = (lat1, lon1, lat2, lon2) => {
  if (!lat1 || !lon1 || !lat2 || !lon2) return Infinity;
  
  const R = 6371;
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}
</script>

<template>
  <div class="home-container">
    <header class="home-header">
      <SearchBar 
        v-model:filtroTipo="filtroTipo" 
        v-model:filtroFechaInicio="filtroFechaInicio" 
        v-model:filtroFechaFin="filtroFechaFin" 
        :categorias="mainStore.categorias"
        :usandoUbicacion="usandoCercania"
        @activarCercania="conmutarFiltroCercania"
      />
    </header>

    <main class="main-layout" :class="{ 'modo-mapa-movil': $route.query.vista === 'mapa' }">
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
    
    <FooterMEC />
    
  </div>
</template>