<script setup>
import { computed } from 'vue'
import { useMainStore } from '../stores/main'
import noImagePlaceholder from '../assets/noImagen.png'
import { CATEGORIAS_MEC } from '../constants/mercadillos'
import '../css/EventoCard.css'

const props = defineProps({
  evento: { type: Object, required: true }
})

const mainStore = useMainStore()

const esFavorito = computed(() => {
  return mainStore.favoritos.some(f => f.id_evento === props.evento.id_evento)
})

const toggleFavorito = () => {
  mainStore.toggleFavorito(props.evento.id_evento)
}

const infoCategoria = computed(() => {
  const categoriaConstante = CATEGORIAS_MEC[props.evento.id_categoria]

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
  return new Date(fechaStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

const imagenPortada = computed(() => {
  if (!props.evento.foto_url) return noImagePlaceholder;
  return props.evento.foto_url.split(',')[0];
})
</script>

<template>
  <article class="evento-card" @click="$emit('click')">
    <div class="image-wrapper">
      
      <button 
        class="fav-btn" 
        :class="{ 'is-fav': esFavorito }" 
        @click.stop="toggleFavorito"
      >
        {{ esFavorito ? '❤️' : '🤍' }}
      </button>

      <img 
        :src="imagenPortada" 
        :alt="evento.titulo"
        class="evento-img"
      />

      <span 
        class="badge" 
        :style="{ backgroundColor: infoCategoria.color }"
      >
        {{ infoCategoria.nombre }}
      </span>
    </div>

    <div class="content">
      <h3 class="title">{{ evento.titulo }}</h3>
      
      <div class="footer">
        <span>📍 {{ evento.direccion_texto }}</span>
        <span v-if="evento.fecha_inicio">🗓️ {{ formatearFecha(evento.fecha_inicio) }}</span>
      </div>
    </div>
  </article>
</template>