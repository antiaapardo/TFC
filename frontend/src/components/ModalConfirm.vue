<script setup>
import '../css/ModalConfirm.css'
defineProps({
  titulo: { type: String, default: '¿Estás seguro?' },
  mensaje: { type: String, default: 'Esta acción no se puede deshacer.' },
  textoConfirmar: { type: String, default: 'Sí, eliminar' },
  textoCancelar: { type: String, default: 'Cancelar' },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: '' }
})

const emit = defineEmits(['confirmar', 'cancelar'])
</script>

<template>
  <div class="confirm-overlay">
    <div class="confirm-card">
      <div class="confirm-icon">⚠️</div>
      
      <h3>{{ titulo }}</h3>
      <p>{{ mensaje }}</p>
      
      <div v-if="error" class="error-msg">
        {{ error }}
      </div>

      <div class="confirm-actions">
        <button class="btn-cancel" @click="emit('cancelar')" :disabled="isLoading">
          {{ textoCancelar }}
        </button>
        <button class="btn-danger" @click="emit('confirmar')" :disabled="isLoading">
          {{ isLoading ? 'Procesando...' : textoConfirmar }}
        </button>
      </div>
    </div>
  </div>
</template>
