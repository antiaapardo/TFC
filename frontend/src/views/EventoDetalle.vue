<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '../stores/main'
import { CATEGORIAS_MEC } from '../constants/mercadillos'
import FooterMEC from '../components/FooterMEC.vue';
import noImagePlaceholder from '../assets/noImagen.png' 
import '../css/EventoDetalle.css';

const route = useRoute()
const router = useRouter()
const mainStore = useMainStore()

const idEvento = Number(route.params.id)
const cargandoData = ref(true)

const fotoActualIndex = ref(0)

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
  const categoriaConstante = CATEGORIAS_MEC[evento.value.id_categoria]
  if (categoriaConstante) {
    return { 
      nombre: categoriaConstante.nombre, 
      color: categoriaConstante.color 
    }
  }
  return { nombre: 'Evento', color: '#717171' }
})

const formatearFecha = (fechaStr) => {
  if (!fechaStr) return ''
  const date = new Date(fechaStr)
  
  const opcionesFecha = { weekday: 'long', day: 'numeric', month: 'long' }
  const fecha = date.toLocaleDateString('es-ES', opcionesFecha)
  
  const opcionesHora = { hour: '2-digit', minute: '2-digit' }
  const hora = date.toLocaleTimeString('es-ES', opcionesHora)
  
  return `${fecha} a las ${hora}`
}

const listaFotos = computed(() => {
  if (!evento.value || !evento.value.foto_url) return [noImagePlaceholder]
  return evento.value.foto_url.split(',').map(url => url.trim()).filter(url => url !== '')
})

const siguienteFoto = () => {
  if (fotoActualIndex.value < listaFotos.value.length - 1) {
    fotoActualIndex.value++
  } else {
    fotoActualIndex.value = 0
  }
}

const fotoAnterior = () => {
  if (fotoActualIndex.value > 0) {
    fotoActualIndex.value--
  } else {
    fotoActualIndex.value = listaFotos.value.length - 1
  }
}
</script>

<template>
  <div class="detalle-page">


    <div v-if="cargandoData" class="loading-state">
      ⏳ Cargando todos los detalles...
    </div>

    <div class="hero-card" v-else-if="evento">
      
      <div class="image-section">
        
        <div class="carousel-container">
          <img :src="listaFotos[fotoActualIndex]" :alt="evento.titulo" class="main-image" />
          
          <span class="badge" :style="{ backgroundColor: infoCategoria.color }">
            {{ infoCategoria.nombre }}
          </span>

          <template v-if="listaFotos.length > 1">
            <button class="carousel-btn prev-btn" @click.stop="fotoAnterior">❮</button>
            <button class="carousel-btn next-btn" @click.stop="siguienteFoto">❯</button>

            <div class="carousel-dots">
              <span 
                v-for="(foto, index) in listaFotos" 
                :key="index" 
                class="dot" 
                :class="{ active: index === fotoActualIndex }"
                @click="fotoActualIndex = index"
              ></span>
            </div>
          </template>
        </div>
        
      </div>

      <div class="info-section">
        <h1 class="title">{{ evento.titulo }}</h1>
        
        <div class="quick-info">
          <div class="info-pill">
            <span class="emoji">🗓️</span>
            <div>
              <strong>Fecha y hora del evento</strong>
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
    <FooterMEC />
</template>