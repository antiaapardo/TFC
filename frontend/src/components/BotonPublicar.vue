<script setup>
import '../css/BotonPublicar.css'

defineProps({
  label: {
    type: String,
    default: 'Publicar nuevo'
  }
})

defineEmits(['click'])
</script>

<template>
  <button class="create-btn" @click="$emit('click')">
    <span class="icon">➕</span>
    {{ label }}
  </button>
</template>