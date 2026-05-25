<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '../stores/main'

import '../css/VerificarCuenta.css'

const route = useRoute()
const router = useRouter()
const mainStore = useMainStore()

const mensaje = ref('Verificando tu cuenta...')
const exito = ref(false)
const cargando = ref(true)

onMounted(async () => {
  const token = route.params.token
  
  if (token) {
    const resultado = await mainStore.verificarCuentaStore(token)
    
    exito.value = resultado.success
    mensaje.value = resultado.msg
  } else {
    exito.value = false
    mensaje.value = 'No se ha encontrado ningún código de verificación.'
  }
  
  cargando.value = false 
})

const irALogin = () => {
  router.push('/login') 
}
</script>

<template>
  <div class="verificar-container">
    <div class="verificar-card">
      
      <div class="icono-estado">
        <span v-if="cargando">⏳</span>
        <span v-else-if="exito">✅</span>
        <span v-else>❌</span>
      </div>

      <h2 :class="{'texto-exito': exito && !cargando, 'texto-error': !exito && !cargando}">
        {{ cargando ? 'Verificando...' : (exito ? '¡Cuenta Verificada!' : 'Aviso de Verificación') }}
      </h2>
      
      <p class="mensaje-texto">{{ mensaje }}</p>
      
      <button v-if="exito && !cargando" @click="irALogin" class="btn-login">
        Ir a Iniciar Sesión
      </button>
      
      <button v-if="!exito && !cargando" @click="router.push('/')" class="btn-volver">
        Volver al inicio
      </button>

    </div>
  </div>
</template>