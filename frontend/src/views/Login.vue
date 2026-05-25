<script setup>
import { ref, reactive } from 'vue'
import { useMainStore } from '../stores/main'
import { useRouter } from 'vue-router'

import '../css/Login.css'

const mainStore = useMainStore()
const router = useRouter()

const isLogin = ref(true)

const form = reactive({
  nombre_completo: '',
  email: '',
  password: '',
  telefono: '',
  tipo_usuario: 'visitante'
})

const mensajeError = ref('')
const mensajeExito = ref('')    

const cambiarModo = (modoLogin) => {
  isLogin.value = modoLogin;
  mensajeError.value = '';
  mensajeExito.value = '';
  form.password = '';
}

const handleSubmit = async () => {
  mensajeError.value = ''
  mensajeExito.value = ''
  
  if (isLogin.value) {
    const exito = await mainStore.loginUsuario(form.email, form.password)
    
    if (exito) {
      router.push('/')
    } else {
      mensajeError.value = mainStore.lastError || 'Credenciales incorrectas'
    }
  } else {
    const exito = await mainStore.registrarUsuario({ ...form })
    
    if (exito) {
      isLogin.value = true
      form.password = '' 
      mensajeExito.value = "¡Registro casi listo! 📧 Te hemos enviado un email. Por favor, revisa tu bandeja de entrada y verifica tu cuenta antes de iniciar sesión."
    } else {
      mensajeError.value = mainStore.lastError || 'Error al registrar usuario'
    }
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      
      <div class="auth-tabs">
        <button 
          :class="{ active: isLogin }" 
          @click="cambiarModo(true)"
        >Iniciar Sesión</button>
        <button 
          :class="{ active: !isLogin }" 
          @click="cambiarModo(false)"
        >Registrarse</button>
      </div>

      <h2 class="auth-title">{{ isLogin ? '¡Hola de nuevo!' : 'Crea tu cuenta' }}</h2>
      <p class="auth-subtitle">
        {{ isLogin ? 'Entra para gestionar tus mercadillos' : 'Únete a la comunidad de economía circular' }}
      </p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        
        <div v-if="!isLogin" class="form-group">
          <label>Nombre Completo</label>
          <input v-model="form.nombre_completo" type="text" placeholder="Tu nombre" required />
        </div>

        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="ejemplo@correo.com" required />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>

        <template v-if="!isLogin">
          <div class="form-group">
            <label>Teléfono (Opcional)</label>
            <input v-model="form.telefono" type="tel" placeholder="600 000 000" />
          </div>

          <div class="form-group">
            <label>¿Qué buscas?</label>
            <select v-model="form.tipo_usuario">
              <option value="visitante">Quiero visitar mercadillos</option>
              <option value="organizador">Quiero organizar mercadillos</option>
            </select>
          </div>
        </template>

        <div v-if="mensajeError" class="error-msg">
          {{ mensajeError }}
        </div>
        <div v-if="mensajeExito" class="success-msg">
          {{ mensajeExito }}
        </div>

        <button type="submit" class="btn-auth" :disabled="mainStore.isLoading">
          {{ mainStore.isLoading ? 'Procesando...' : (isLogin ? 'Entrar' : 'Registrarme') }}
        </button>
      </form>

    </div>
  </div>
</template>