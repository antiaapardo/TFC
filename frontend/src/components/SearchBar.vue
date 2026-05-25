<script setup>
import '../css/searchBar.css'
defineProps({
  filtroTipo: String,
  filtroFechaInicio: String,
  filtroFechaFin: String,   
  categorias: Array,
  usandoUbicacion: Boolean
})

defineEmits([
  'update:filtroTipo', 
  'update:filtroFechaInicio', 
  'update:filtroFechaFin',    
  'activarCercania'
])
</script>

<template>
  <div class="search-container">
    <div class="search-bar">
      
      <div class="search-item">
        <label>¿Qué buscas?</label>
        <select :value="filtroTipo" @input="$emit('update:filtroTipo', $event.target.value)">
          <option value="">Todos los eventos</option>
          <option v-for="cat in categorias" :key="cat.id_categoria" :value="cat.id_categoria">
            {{ cat.nombre }}
          </option>
        </select>
      </div>

      <div class="divider"></div>

<div class="search-item date-range-item">
        <label>¿Cuándo?</label>
        <div class="date-inputs">
          <div class="date-input-group">
            <span class="date-sublabel">Desde</span>
            <input 
              type="date" 
              :value="filtroFechaInicio" 
              @input="$emit('update:filtroFechaInicio', $event.target.value)"
            />
          </div>
          
          <div class="date-input-group">
            <span class="date-sublabel">Hasta</span>
            <input 
              type="date" 
              :value="filtroFechaFin" 
              @input="$emit('update:filtroFechaFin', $event.target.value)"
            />
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <button 
        type="button" 
        class="cercania-btn" 
        :class="{ 'activo': usandoUbicacion }"
        @click="$emit('activarCercania')"
      >
        <span class="pin-icon">📍</span>
        <span class="cercania-text">
          {{ usandoUbicacion ? 'Mostrando cerca de mi' : 'Cerca de mí' }}
        </span>
      </button>

      <button class="search-btn" type="button">
        🔍
      </button>
      
    </div>
  </div>
</template>