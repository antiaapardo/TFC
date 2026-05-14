<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '../stores/main'
import { CATEGORIAS_MEC } from '../constants/mercadillos'
import noImagePlaceholder from '../assets/noImagen.png'
import '../css/EventoDetalle.css';

const route = useRoute()
const router = useRouter()
const mainStore = useMainStore()

const idEvento = route.params.id
const cargandoData = ref(true)

onMounted(async () => {
  if (!mainStore.eventos || mainStore.eventos.length === 0) {
    await mainStore.fetchEventos()
  }
  if (mainStore.currentUser && mainStore.favoritos.length === 0) {
    await mainStore.fetchFavoritos()
  }
  cargandoData.value = false
})

const evento = computed(() => {
  if (!mainStore.eventos) return null
  return mainStore.eventos.find(e => e.id_evento == idEvento)
})
const esFavorito = computed(() => {
  return mainStore.favoritos.some(f => f.id_evento == idEvento)
})

const handleToggleFavorito = async () => {
  if (!mainStore.currentUser) {
    router.push('/login')
    return
  }
  
  await mainStore.toggleFavorito(idEvento)
}

const infoCategoria = computed(() => {
  if (!evento.value) return { nombre: 'Evento', color: '#717171' }
  const categoriaReal = mainStore.categorias.find(c => c.id_categoria == evento.value.id_categoria)
  return categoriaReal ? 
    { nombre: categoriaReal.nombre, color: CATEGORIAS_MEC[evento.value.id_categoria]?.color || '#E10818' } : 
    { nombre: 'Evento', color: '#717171' }
})

const formatearFecha = (fechaStr) => {
  if (!fechaStr) return ''
  return new Date(fechaStr).toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
}
</script>

<template>
  <div class="detalle-page">
    
    <div class="nav-top">
      <button @click="router.back()" class="btn-back">
        <span class="icon">←</span> Volver a explorar
      </button>
    </div>

    <div v-if="cargandoData" class="loading-state">
      ⏳ Cargando todos los detalles...
    </div>

    <div class="hero-card" v-else-if="evento">
      
      <div class="image-section">
        <img :src="evento.foto_url || noImagePlaceholder" :alt="evento.titulo" class="main-image" />
        <span class="badge" :style="{ backgroundColor: infoCategoria.color }">
          {{ infoCategoria.nombre }}
        </span>
      </div>

      <div class="info-section">
        <h1 class="title">{{ evento.titulo }}</h1>
        
        <div class="quick-info">
          <div class="info-pill">
            <span class="emoji">🗓️</span>
            <div>
              <strong>Fecha del evento</strong>
              <p>{{ formatearFecha(evento.fecha_inicio) }}</p>
            </div>
          </div>
          
          <div class="info-pill">
            <span class="emoji">📍</span>
            <div>
              <strong>Ubicación</strong>
              <p>{{ evento.direccion_texto }}</p>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <div class="description-box">
          <h3>Acerca de este mercadillo</h3>
          <p>{{ evento.descripcion || 'El organizador aún no ha añadido una descripción para este evento.' }}</p>
        </div>

        <div class="action-footer">
          <button 
            @click.stop="handleToggleFavorito"
            class="btn-primary" 
            :class="{ 'is-fav': esFavorito }"
          >
            <span v-if="esFavorito">❤️ Quitar de favoritos</span>
            <span v-else>🤍 Añadir a favoritos</span>
          </button>
        </div>
      </div>
      
    </div>

    <div v-else class="error-state">
      ❌ No hemos podido encontrar este mercadillo.
    </div>

  </div>
</template>

