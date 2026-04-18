<template>
  <div class="dashboard">
    <header class="header">
      <div class="logo-area">
        <img :src="logoImage" alt="Logo MEC" class="main-logo" />
        <div class="title-info">
          <h1>MEC: Mercadillos en Casa 🏠</h1>
          <p class="subtitle">Economía circular en tu barrio</p>
        </div>
      </div>
      
      <nav class="nav-user">
        <button class="nav-btn" title="Favoritos">❤️</button>
        <div class="profile-circle" title="Mi Perfil">A</div>
      </nav>
    </header>

    <section class="search-container">
      <div class="search-bar">
        <div class="search-item">
          <label>¿Qué buscas?</label>
          <select v-model="filtroTipo">
            <option value="">Todos los eventos</option>
            <option v-for="cat in categorias" :key="cat.id_categoria" :value="cat.id_categoria">
              {{ cat.nombre }}
            </option>
          </select>
        </div>
        
        <div class="divider"></div>
        
        <div class="search-item">
          <label>¿Cuándo?</label>
          <input type="date" v-model="filtroFecha" />
        </div>

        <button class="search-btn">🔍</button>
      </div>
    </section>

    <main class="content-split">
      <section class="events-list">
        <div v-for="evento in eventos" :key="evento.id_evento" class="event-card">
          <div class="card-image">
            <img :src="evento.imagen_url || imagenPorDefecto" alt="Mercadillo">
            <button class="wishlist-btn">🤍</button>
          </div>

          <div class="card-info">
            <div class="card-header">
              <h4>{{ evento.titulo }}</h4>
              <span class="rating">★ 4.9</span>
            </div>
            <p class="location">{{ evento.direccion_texto }}</p>
            <p class="date">{{ evento.fecha || 'Próximamente' }}</p>
            <p class="price">
              <strong>{{ evento.precio > 0 ? evento.precio + '€' : 'Entrada gratuita' }}</strong>
            </p>
          </div>
        </div>
      </section>

      <section class="map-sidebar">
        <div class="map-wrapper">
          <MapaInteractivo :eventos="eventos" />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import logoImage from './assets/logoMEC.png'
import MapaInteractivo from './components/MapaInteractivo.vue'
import imagenPorDefecto from './assets/noImagen.png'

const categorias = ref([])
const eventos = ref([])
const filtroTipo = ref('')
const filtroFecha = ref('')

onMounted(async () => {
  try {
    const resCat = await axios.get('http://localhost:3000/api/categorias')
    categorias.value = resCat.data

    const resEve = await axios.get('http://localhost:3000/api/eventos')
    eventos.value = resEve.data
  } catch (error) {
    console.error('❌ Error en la conexión:', error)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 15px;
}

.main-logo {
  height: 60px;
  border-radius: 12px;
}

.title-info h1 {
  margin: 0;
  font-size: 1.5rem;
}

.subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.nav-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.profile-circle {
  width: 40px;
  height: 40px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* SEARCH BAR */
.search-container {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.search-bar {
  display: flex;
  align-items: center;
  background: white;
  padding: 8px 10px 8px 25px;
  border-radius: 100px;
  border: 1px solid #ddd;
  box-shadow: 0 3px 12px rgba(0,0,0,0.08);
  min-width: 500px;
}

.search-item {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.search-item label {
  font-size: 11px;
  font-weight: 800;
}

.search-item select, .search-item input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
}

.divider {
  width: 1px;
  height: 30px;
  background-color: #eee;
  margin: 0 15px;
}

.search-btn {
  background-color: #3498db;
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
}

/* SPLIT VIEW (MAPA + LISTA) */
.content-split {
  display: grid;
  grid-template-columns: 1fr 480px;
  height: calc(100vh - 180px);
  overflow: hidden;
}

.events-list {
  padding: 10px 20px 40px 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  overflow-y: auto;
}

.map-sidebar {
  padding: 10px;
  height: 100%;
}

.map-wrapper {
  width: 100%;
  height: 100%;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.event-card {
  cursor: pointer;
}

.card-image {
  position: relative;
  aspect-ratio: 1/1;
  border-radius: 12px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.wishlist-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}

.card-info h4 {
  margin: 8px 0 2px 0;
  font-size: 1rem;
}

.location, .date {
  margin: 0;
  font-size: 0.85rem;
  color: #717171;
}

.price {
  margin-top: 5px;
  font-size: 0.9rem;
}
</style>