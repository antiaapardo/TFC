<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '../stores/main'

// Imagen por defecto si el usuario no tiene foto
import defaultAvatar from '../assets/noImagen.png' 

const router = useRouter()
const mainStore = useMainStore()

const user = mainStore.currentUser

// VARIABLES REACTIVAS PARA LA FOTO
const fileInput = ref(null) 
const selectedFile = ref(null) 
const previewImage = ref(user?.foto_url || null) 

// FORMULARIO DE DATOS Y CONTRASEÑA
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
  fileInput.value.click()
}

const onFileSelected = (event) => {
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

  selectedFile.value = file

  const reader = new FileReader()
  reader.onload = (e) => {
    previewImage.value = e.target.result 
  }
  reader.readAsDataURL(file)
}

// ==========================================
// LÓGICA DE ACTUALIZACIÓN DE PERFIL BÁSICO
// ==========================================
const handleUpdateInfo = async () => {
  mensajeStatus.value = { texto: '', tipo: '' }
  let exito = true;

  if (selectedFile.value) {
    exito = await mainStore.subirAvatar(selectedFile.value)
  }

  if (exito) {
    const exitoInfo = await mainStore.actualizarPerfil({
      nombre_completo: form.nombre_completo
    })
    
    if (exitoInfo) {
      mensajeStatus.value = { texto: '¡Perfil actualizado con éxito! ✨', tipo: 'exito' }
      selectedFile.value = null 
    } else {
      exito = false
    }
  }

  if (!exito) {
    mensajeStatus.value = { texto: mainStore.lastError || 'Error al actualizar', tipo: 'error' }
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
          <div class="avatar-wrapper" @click="triggerFileInput" title="Pulsa para cambiar la foto">
            <img :src="previewImage || defaultAvatar" alt="Avatar" class="profile-avatar" />
            <div class="edit-overlay">
              <span>📷 Cambiar</span>
            </div>
          </div>
          
          <input 
            type="file" 
            ref="fileInput" 
            style="display: none" 
            accept="image/*" 
            @change="onFileSelected" 
          />
          
          <button type="button" class="btn-outline-sm" @click="triggerFileInput">
            {{ previewImage ? 'Cambiar foto' : 'Añadir foto' }}
          </button>
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
  </div>
</template>

<style scoped>
.edit-profile-page { 
  max-width: 900px; 
  margin: 40px auto; 
  padding: 0 20px; 
  font-family: 'Nunito', sans-serif; 
}

.edit-header { 
  margin-bottom: 30px; 
}

.btn-back { 
  background: none; 
  border: none; 
  color: #666; 
  font-weight: 700; 
  cursor: pointer; 
  margin-bottom: 10px; 
  padding: 0;
}

.btn-back:hover {
  color: #E10818;
}

.edit-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 30px; 
  align-items: start;
}

.edit-section { 
  background: white; 
  padding: 30px; 
  border-radius: 24px; 
  box-shadow: 0 10px 25px rgba(0,0,0,0.03); 
  border: 1px solid #f0f0f0; 
}

.edit-section h3 { 
  margin-top: 0; 
  margin-bottom: 25px; 
  color: #2c3e50; 
}

.form-group { 
  margin-bottom: 20px; 
}

.form-group label { 
  display: block; 
  font-weight: 800; 
  font-size: 0.85rem; 
  color: #7f8c8d; 
  margin-bottom: 8px; 
  text-transform: uppercase; 
}

.form-group input { 
  width: 100%; 
  padding: 12px; 
  border: 2px solid #eee; 
  border-radius: 12px; 
  font-family: inherit; 
  box-sizing: border-box; 
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #2c3e50;
  outline: none;
}

.disabled-input { 
  background: #f9f9f9; 
  color: #999; 
  cursor: not-allowed;
}

.btn-save { 
  width: 100%; 
  padding: 14px; 
  background: #2c3e50; 
  color: white; 
  border: none; 
  border-radius: 12px; 
  font-weight: 800; 
  cursor: pointer; 
  transition: all 0.3s; 
  margin-top: 10px;
}

.btn-save:hover { 
  background: #1a252f; 
  transform: translateY(-2px); 
}

.btn-save:disabled { 
  background: #ccc; 
  cursor: not-allowed; 
  transform: none;
}

.btn-security { 
  background: #E10818; 
}

.btn-security:hover { 
  background: #b90614; 
}

.status-msg { 
  padding: 15px; 
  border-radius: 12px; 
  margin-bottom: 25px; 
  font-weight: 700; 
  text-align: center; 
}

.exito { background: #e8f5e9; color: #2e7d32; }
.error { background: #ffebee; color: #c62828; }

/* ESTILOS DE LA FOTO DE PERFIL */
.avatar-edit-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  border: 4px solid white;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.profile-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 40%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-wrapper:hover .edit-overlay {
  opacity: 1;
}

.btn-outline-sm {
  background: transparent;
  border: 1px solid #ddd;
  color: #555;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
}

.btn-outline-sm:hover {
  border-color: #ccc;
  background-color: #f9f9f9;
}

@media (max-width: 768px) {
  .edit-grid { grid-template-columns: 1fr; }
}
</style>