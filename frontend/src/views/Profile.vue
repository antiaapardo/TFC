<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import ConfirmModal from '../components/ModalConfirm.vue'
import { useRouter } from 'vue-router'
import EventoCard from '../components/EventoCard.vue'
import BotonPublicar from '../components/BotonPublicar.vue'
import ModalPublicar from '../components/ModalPublicar.vue'

import '../css/Profile.css'

const mainStore = useMainStore()
const mostrarModal = ref(false)
const router = useRouter()

onMounted(() => {
  if (!mainStore.eventos || mainStore.eventos.length === 0) {
    mainStore.fetchEventos()
  }
})
const irADetalle = (idEvento) => {
  router.push(`/evento/${idEvento}`)
}
const esOrganizador = computed(() => {
  return mainStore.currentUser?.tipo_usuario === 'organizador'
})

const misEventos = computed(() => {
  if (!mainStore.eventos || !mainStore.currentUser) return []
  return mainStore.eventos.filter(evento => 
    evento.id_organizador === mainStore.currentUser.id_usuario || 
    evento.id_usuario === mainStore.currentUser.id_usuario
  )
})

const cargarEventos = async () => {
  await mainStore.fetchEventos()
  mostrarModal.value = false
}

const mostrarConfirmacion = ref(false)
const eventoABorrar = ref(null)
const errorBorrado = ref('') 

const solicitarBorrado = (idEvento) => {
  eventoABorrar.value = idEvento
  errorBorrado.value = '' 
  mostrarConfirmacion.value = true
}

const cancelarBorrado = () => {
  mostrarConfirmacion.value = false
  eventoABorrar.value = null
  errorBorrado.value = ''
}

const confirmarBorrado = async () => {
  errorBorrado.value = ''
  if (eventoABorrar.value) {
    const exito = await mainStore.eliminarEvento(eventoABorrar.value)
    if (!exito) {
      errorBorrado.value = mainStore.lastError || "Hubo un problema al eliminar el mercadillo."
      return 
    }
  }
  mostrarConfirmacion.value = false
  eventoABorrar.value = null
}
</script>

<template>
  <div class="profile-page-container">
    
    <header class="profile-banner">
      <div class="banner-user-info">
        <div class="banner-avatar" style="overflow: hidden; padding: 0;">
          <img 
            v-if="mainStore.currentUser?.foto_url" 
            :src="mainStore.currentUser.foto_url" 
            style="width: 100%; height: 100%; object-fit: cover;" 
          />
          <span v-else>
            {{ mainStore.currentUser?.nombre_completo?.charAt(0).toUpperCase() || 'U' }}
          </span>
        </div>
        <div class="banner-text">
          <h2>{{ mainStore.currentUser?.nombre_completo || 'Usuario' }}</h2>
          <p class="banner-email">{{ mainStore.currentUser?.email }}</p>
          <span class="banner-badge">{{ esOrganizador ? 'Organizador MEC' : 'Visitante MEC' }}</span>
        </div>
      </div>
      <div class="banner-actions">
        <router-link to="/profile/edit">
          <button class="btn-outline">Editar Perfil</button>
        </router-link>
      </div>
    </header>

    <main class="profile-full-content">

      <template v-if="esOrganizador">
        <div class="content-header">
          <h3 class="section-title">Mis Mercadillos publicados</h3>
          <BotonPublicar @click="mostrarModal = true" class="btn-custom-style" />
        </div>

        <div class="events-grid">
          <div v-for="evento in misEventos" :key="evento.id_evento" class="evento-wrapper">
            
            <EventoCard 
              :evento="evento" 
              @click="irADetalle(evento.id_evento)" 
            />
            
            <button @click="solicitarBorrado(evento.id_evento)" class="btn-eliminar">
              🗑️ Eliminar Mercadillo
            </button>
          </div>
          
          <div v-if="misEventos.length === 0" class="empty-placeholder">
            <p>Aún no has publicado ningún mercadillo.</p>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="content-header">
          <h3 class="section-title">¡Hola, {{ mainStore.currentUser?.nombre_completo?.split(' ')[0] || 'Visitante' }}!</h3>
        </div>
        
        <div class="welcome-panel">
          <div class="welcome-icon">🗺️</div>
          <div class="welcome-text">
            <h4>Tu panel de control</h4>
            <p>
              Como visitante, puedes explorar el mapa de economía circular en tu barrio y guardar tus mercadillos favoritos para no perderte ninguna ganga.
            </p>
            <router-link to="/favoritos" class="welcome-link">
              <button class="btn-welcome">
                Ver mis mercadillos guardados ❤️
              </button>
            </router-link>
          </div>
        </div>
      </template>

      <ModalPublicar 
        v-if="mostrarModal && esOrganizador" 
        @close="mostrarModal = false" 
        @actualizar="cargarEventos" 
      />

      <div v-if="mostrarConfirmacion && esOrganizador" class="confirm-overlay">
        <ConfirmModal 
          titulo="¿Eliminar mercadillo?" 
          mensaje="Esta acción no se puede deshacer. Desaparecerá de tu perfil y del mapa principal."
          :error="errorBorrado"
          :isLoading="mainStore.isLoading"
          @confirmar="confirmarBorrado" 
          @cancelar="cancelarBorrado" 
        />
      </div>

    </main>
  </div>
</template>