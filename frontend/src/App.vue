<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from './stores/main' // Asegúrate de que esta ruta es correcta
import logoImage from './assets/logoMEC.png'

import './css/App.css'

const mainStore = useMainStore()
const router = useRouter()

const menuAbierto = ref(false)

const toggleMenu = () => {
  menuAbierto.value = !menuAbierto.value
}

const handleLogout = () => {
  mainStore.cerrarSesion()
  menuAbierto.value = false 
  router.push('/')
}
</script>

<template>
  <div id="app">
    <header class="header">
      
      <router-link to="/" class="logo-area" style="text-decoration: none; cursor: pointer;">
        <img :src="logoImage" alt="Logo MEC" class="main-logo" />
        <div class="title-info">
          <h1 style="color: #222;">MEC: Mercadillos en Casa</h1>
          <p class="subtitle">Economía circular en tu barrio</p>
        </div>
      </router-link>
      
      <nav class="nav-user">
        
        <router-link 
          to="/favoritos"
          class="nav-btn" 
          title="Mis Favoritos"
          style="text-decoration: none;"
        >
          ❤️
        </router-link>

        <div v-if="mainStore.currentUser" class="dropdown-container">
          
          <div class="profile-circle" @click="toggleMenu" style="cursor: pointer; overflow: hidden; padding: 0; display: flex; align-items: center; justify-content: center;">
            
            <img 
              v-if="mainStore.currentUser?.foto_url" 
              :src="mainStore.currentUser.foto_url" 
              style="width: 100%; height: 100%; object-fit: cover;"
              alt="Avatar"
            />
            
            <span v-else>
              {{ mainStore.currentUser?.nombre_completo?.charAt(0).toUpperCase() || 'U' }}
            </span>
          </div>

          <div v-if="menuAbierto" class="dropdown-menu">
            <div class="dropdown-header">
              <strong>{{ mainStore.currentUser?.nombre_completo || 'Usuario' }}</strong>
              <span>{{ mainStore.currentUser?.email || '' }}</span>
            </div>
            
            <hr>
            
            <router-link to="/profile" class="dropdown-item" @click="menuAbierto = false">
              👤 Mi Perfil
            </router-link>
            
            <button class="dropdown-item" @click="menuAbierto = false">
              ⚙️ Configuración
            </button>
            
            <hr>
            
            <button class="dropdown-item logout-item" @click="handleLogout">
              🚪 Cerrar Sesión
            </button>
          </div>
        </div>

        <router-link 
          v-else 
          to="/login" 
          class="profile-circle" 
          title="Iniciar Sesión"
          style="background-color: #666; display: flex; align-items: center; justify-content: center; text-decoration: none;"
        >
          👤
        </router-link>

      </nav>
    </header>

    <router-view />

    <nav class="bottom-nav">
      <router-link to="/" class="bottom-nav-item" :class="{ 'icono-activo': $route.path === '/' && !$route.query.vista }">
        <span class="nav-icon">🔍</span>
        <span>Explorar</span>
      </router-link>
      
      <router-link to="/?vista=mapa" class="bottom-nav-item" :class="{ 'icono-activo': $route.query.vista === 'mapa' }">
        <span class="nav-icon">🗺️</span>
        <span>Mapa</span>
      </router-link>
      
      <router-link to="/favoritos" class="bottom-nav-item" :class="{ 'icono-activo': $route.path === '/favoritos' }">
        <span class="nav-icon">❤️</span>
        <span>Favoritos</span>
      </router-link>
      
      <router-link :to="mainStore.currentUser ? '/profile' : '/login'" class="bottom-nav-item" :class="{ 'icono-activo': $route.path === '/profile' || $route.path === '/login' }">
        
        <div v-if="mainStore.currentUser" class="profile-circle-nav">
          <img 
            v-if="mainStore.currentUser?.foto_url" 
            :src="mainStore.currentUser.foto_url" 
            alt="Avatar"
          />
          <span v-else>
            {{ mainStore.currentUser?.nombre_completo?.charAt(0).toUpperCase() || 'U' }}
          </span>
        </div>

        <span v-else class="nav-icon">👤</span>
        
        <span v-if="mainStore.currentUser">Perfil</span>
        <span v-else>Entrar</span>
      </router-link>
    </nav>

  </div>
</template>