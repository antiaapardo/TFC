
<script setup>
import '../css/UsuarioCard.css'

defineProps({
  nombre: String,
  email: String,
  inicial: String,
  badge: {
    type: String,
    default: 'Anfitrión MEC'
  }
})

defineEmits(['edit'])
</script>
<template>
  <div class="profile-card">
    <div class="avatar-wrapper">
      <div class="avatar-main">{{ inicial }}</div>
      <button class="change-photo-btn" title="Cambiar foto">📸</button>
    </div>
    
    <h2 class="user-name">{{ nombre }}</h2>
    <p class="user-badge">{{ badge }}</p>
    <p class="user-email">{{ email }}</p>
    
    <button class="primary-outline-btn" @click="$emit('edit')">
      Editar Perfil
    </button>
  </div>
</template>
