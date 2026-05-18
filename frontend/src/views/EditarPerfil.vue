<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '../stores/main'
import ConfirmModal from '../components/ModalConfirm.vue'

import '../css/EditarPerfil.css';
import defaultAvatar from '../assets/noImagen.png' 

const router = useRouter()
const mainStore = useMainStore()

const user = mainStore.currentUser

const fileInput = ref(null) 
const selectedFile = ref(null) 
const previewImage = ref(user?.foto_url || null) 
const mostrarModalFoto = ref(false)
const subiendoFoto = ref(false)
const isMenuFotoOpen = ref(false)

const form = reactive({
  nombre_completo: user?.nombre_completo || '',
  email: user?.email || '',
  password_actual: '',
  password_nueva: '',
  password_confirmar: ''
})

const mensajeStatus = ref({ texto: '', tipo: '' })

// ==========================================
// LÓGICA DE FOTO DE PERFIL
// ==========================================
const triggerFileInput = () => {
  isMenuFotoOpen.value = false
  fileInput.value.click()
}

const onFileSelected = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    mensajeStatus.value = { texto: 'Por favor, selecciona una imagen válida (jpg, png).', tipo: 'error' }
    return
  }
  if (file.size > 2 * 1024 * 1024) { 
    mensajeStatus.value = { texto: 'La imagen es demasiado grande (máx 2MB).', tipo: 'error' }
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => { previewImage.value = e.target.result }
  reader.readAsDataURL(file)

  subiendoFoto.value = true
  isMenuFotoOpen.value = false // Cerramos el menú
  mensajeStatus.value = { texto: 'Subiendo foto de perfil... ⏳', tipo: 'info' }

  const exito = await mainStore.subirAvatar(file)

  if (exito) {
    mensajeStatus.value = { texto: '¡Foto de perfil actualizada! 📸', tipo: 'exito' }
    previewImage.value = mainStore.currentUser.foto_url 
  } else {
    mensajeStatus.value = { texto: mainStore.lastError || 'Error al subir la foto', tipo: 'error' }
    previewImage.value = mainStore.currentUser.foto_url || defaultAvatar
  }

  subiendoFoto.value = false
  
  if (fileInput.value) fileInput.value.value = ''
}

const solicitarBorradoFoto = () => {
  isMenuFotoOpen.value = false 
  mostrarModalFoto.value = true 
}

const confirmarBorradoFoto = async () => {
  console.log("👉 1. Botón del modal pulsado");
  
  if (typeof mainStore.eliminarAvatar !== 'function') {
    return;
  }

  console.log("👉 2. Llamando a la base de datos...");
  const exito = await mainStore.eliminarAvatar()
  
  console.log("👉 3. Resultado:", exito);
  if (exito) {
    mensajeStatus.value = { texto: 'Foto eliminada con éxito ✨', tipo: 'exito' }
    previewImage.value = null 
    selectedFile.value = null
  } else {
    mensajeStatus.value = { texto: 'Error al eliminar la foto', tipo: 'error' }
  }
  
  mostrarModalFoto.value = false // Cierra el modal
}

// ==========================================
// LÓGICA DE ACTUALIZACIÓN DE PERFIL BÁSICO
// ==========================================

const handleUpdateInfo = async () => {
  mensajeStatus.value = { texto: '', tipo: '' }
  
  const exitoInfo = await mainStore.actualizarPerfil({
    nombre_completo: form.nombre_completo
  })
  
  if (exitoInfo) {
    mensajeStatus.value = { texto: '¡Datos básicos actualizados con éxito! ✨', tipo: 'exito' }
  } else {
    mensajeStatus.value = { texto: mainStore.lastError || 'Error al actualizar el perfil', tipo: 'error' }
  }
}

// ==========================================
// LÓGICA DE CAMBIO DE CONTRASEÑA
// ==========================================
const handleChangePassword = async () => {
  mensajeStatus.value = { texto: '', tipo: '' }

  if (!form.password_actual || !form.password_nueva || !form.password_confirmar) {
    mensajeStatus.value = { texto: 'Por favor, rellena todos los campos de contraseña.', tipo: 'error' }
    return
  }

  if (form.password_nueva !== form.password_confirmar) {
    mensajeStatus.value = { texto: 'Las contraseñas nuevas no coinciden ❌', tipo: 'error' }
    return
  }

  const exito = await mainStore.cambiarPassword({
    actual: form.password_actual,
    nueva: form.password_nueva
  })

  if (exito) {
    mensajeStatus.value = { texto: 'Contraseña cambiada correctamente 🔐', tipo: 'exito' }
    form.password_actual = ''
    form.password_nueva = ''
    form.password_confirmar = ''
  } else {
    mensajeStatus.value = { texto: mainStore.lastError || 'Error al cambiar la contraseña.', tipo: 'error' }
  }
}
</script>

<template>
  <div class="edit-profile-page">
    <div class="edit-header">
      <button @click="router.back()" class="btn-back">← Cancelar y volver</button>
      <h1>Editar mi perfil</h1>
    </div>

    <div v-if="mensajeStatus.texto" :class="['status-msg', mensajeStatus.tipo]">
      {{ mensajeStatus.texto }}
    </div>

    <div class="edit-grid">
      
      <section class="edit-section info-section">
        <h3>Información Personal</h3>
        
        <div class="avatar-edit-container">
          <div class="avatar-wrapper" @click="isMenuFotoOpen = !isMenuFotoOpen" title="Pulsa para opciones de foto">
            <img :src="previewImage || defaultAvatar" alt="Avatar" class="profile-avatar" />
            <div class="edit-overlay">
              <span>{{ subiendoFoto ? '⏳ Subiendo...' : '📷 Opciones' }}</span>
            </div>
          </div>
          
          <input 
            type="file" 
            ref="fileInput" 
            style="display: none" 
            accept="image/*" 
            @change="onFileSelected" 
          />
          
          <div class="avatar-actions-container">
            <button type="button" class="btn-edit-avatar" @click.prevent="isMenuFotoOpen = !isMenuFotoOpen">
              📷 Editar foto de perfil
            </button>

            <div v-if="isMenuFotoOpen" class="avatar-dropdown">
              <button class="dropdown-item" @click.prevent="triggerFileInput">
                📷 Subir foto de perfil
              </button>
              
              <button class="dropdown-item delete-text" @click.prevent="solicitarBorradoFoto">
                🗑️ Eliminar foto de perfil
              </button>
            </div>
          </div>

        </div>

        <div class="form-group">
          <label>Nombre Completo</label>
          <input v-model="form.nombre_completo" type="text" required />
        </div>
        
        <div class="form-group">
          <label>Email (No editable)</label>
          <input v-model="form.email" type="email" disabled class="disabled-input" />
        </div>
        
        <button @click="handleUpdateInfo" class="btn-save" :disabled="mainStore.isLoading">
          {{ mainStore.isLoading ? 'Guardando...' : 'Guardar cambios básicos' }}
        </button>
      </section>

      <section class="edit-section">
        <h3>Seguridad</h3>
        
        <div class="form-group">
          <label>Contraseña Actual</label>
          <input v-model="form.password_actual" type="password" placeholder="Tu contraseña actual" />
        </div>
        
        <div class="form-group">
          <label>Nueva Contraseña</label>
          <input v-model="form.password_nueva" type="password" placeholder="Mínimo 6 caracteres" />
        </div>
        
        <div class="form-group">
          <label>Confirmar Nueva Contraseña</label>
          <input v-model="form.password_confirmar" type="password" placeholder="Repite la nueva contraseña" />
        </div>
        
        <button @click="handleChangePassword" class="btn-save btn-security" :disabled="mainStore.isLoading">
          Actualizar contraseña
        </button>
      </section>
      
    </div>
    <ConfirmModal 
  v-if="mostrarModalFoto" 
  titulo="¿Eliminar foto de perfil?" 
  mensaje="Tu foto desaparecerá y se mostrará la inicial de tu nombre por defecto."
  :isLoading="mainStore.isLoading"
  @confirmar="confirmarBorradoFoto" 
  @cancelar="mostrarModalFoto = false" 
/>
  </div>
</template>