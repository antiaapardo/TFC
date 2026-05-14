<script setup>
import { computed } from 'vue'
import { useMainStore } from '../stores/main' // Importamos el store
import noImagePlaceholder from '../assets/noImagen.png'
import { CATEGORIAS_MEC } from '../constants/mercadillos'

// Importamos el CSS específico
import '../css/EventoCard.css'

const props = defineProps({
  evento: { type: Object, required: true }
})

const mainStore = useMainStore()

// LÓGICA DE FAVORITOS (Reactiva a Pinia)
const esFavorito = computed(() => {
  return mainStore.favoritos.some(f => f.id_evento === props.evento.id_evento)
})

const toggleFavorito = () => {
  mainStore.toggleFavorito(props.evento.id_evento)
}

const infoCategoria = computed(() => {
  // 1. Buscamos la categoría en la lista oficial que nos bajamos de la Base de Datos
  const categoriaReal = mainStore.categorias.find(c => c.id_categoria == props.evento.id_categoria)

  // 2. Si la encontramos, mostramos su nombre. 
  if (categoriaReal) {
    return { 
      nombre: categoriaReal.nombre, 
      // Si tienes un color en CATEGORIAS_MEC puedes cogerlo así, si no, usamos el rojo MEC
      color: CATEGORIAS_MEC[props.evento.id_categoria]?.color || '#E10818' 
    }
  }

  // 3. Fallback de seguridad por si hay algún error
  return { nombre: 'Evento', color: '#717171' }
})

const formatearFecha = (fechaStr) => {
  if (!fechaStr) return ''
  return new Date(fechaStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}
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
        :src="evento.foto_url || noImagePlaceholder" 
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
      <p class="description">{{ evento.descripcion }}</p>
      
      <div class="footer">
        <span>📍 {{ evento.direccion_texto }}</span>
        <span v-if="evento.fecha_inicio">🗓️ {{ formatearFecha(evento.fecha_inicio) }}</span>
      </div>
    </div>
  </article>
</template>