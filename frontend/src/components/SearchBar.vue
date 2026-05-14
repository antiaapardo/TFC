<script setup>
import '../css/SearchBar.css'

defineProps({
  categorias: {
    type: Array,
    default: () => []
  },
  filtroTipo: [String, Number],
  filtroFecha: String
})

defineEmits(['update:filtroTipo', 'update:filtroFecha', 'buscar'])
</script>

<template>
  <section class="search-container">
    <div class="search-bar">
      
      <div class="search-item">
        <label>¿Qué buscas?</label>
        <select 
          :value="filtroTipo" 
          @change="$emit('update:filtroTipo', $event.target.value)"
        >
          <option value="">Todos los eventos</option>
          <option 
            v-for="cat in categorias" 
            :key="cat.id_categoria" 
            :value="cat.id_categoria"
          >
            {{ cat.nombre }}
          </option>
        </select>
      </div>

      <div class="divider"></div>

      <div class="search-item">
        <label>¿Cuándo?</label>
        <input 
          type="date" 
          :value="filtroFecha" 
          @input="$emit('update:filtroFecha', $event.target.value)" 
        />
      </div>

      <button class="search-btn" @click="$emit('buscar')">
        🔍
      </button>
      
    </div>
  </section>
</template>