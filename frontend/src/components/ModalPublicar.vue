<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import '../css/ModalPublicar.css'

const emit = defineEmits(['close', 'actualizar'])
const mainStore = useMainStore()

const isSubmitting = ref(false)
const mensaje = ref('')
const tipoMensaje = ref('')
const selectedFiles = ref([])

onMounted(() => {
  if (mainStore.categorias.length === 0) {
    mainStore.fetchCategorias()
  }
})

const form = reactive({
  id_usuario: mainStore.userId, 
  titulo: '',
  id_categoria: '',
  direccion_texto: '',
  fecha_inicio: '',
  latitud: null,
  longitud: null,
  descripcion: 'Nuevo mercadillo de economía circular.', 
  foto_url: '' 
})

const onFilesSelected = (event) => {
  const files = Array.from(event.target.files)
  
  // Filtramos para asegurarnos de que solo sean imágenes
  selectedFiles.value = files.filter(file => file.type.startsWith('image/'))
}

const obtenerCoordenadas = async (direccion) => {
  try {
    let textoBusqueda = direccion.trim();
    
    if (!textoBusqueda.toLowerCase().includes('madrid')) {
      textoBusqueda = `${textoBusqueda}, Madrid`;
    }
    
    const queryBusqueda = `${textoBusqueda}, España`;
    console.log("🔍 Buscando en el mapa:", queryBusqueda);
    
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryBusqueda)}&limit=1&countrycodes=es&addressdetails=1`;
    
    const respuesta = await fetch(url, {
      headers: { 'Accept-Language': 'es' }
    });
    const datos = await respuesta.json();
    
    if (datos && datos.length > 0) {
      const resultado = datos[0];
      return { 
        lat: parseFloat(resultado.lat), 
        lon: parseFloat(resultado.lon) 
      }
    }
  } catch (error) {
    console.error("❌ Error en la geocodificación:", error)
  }
  return null
}

// ¡AQUÍ ESTABA EL FALLO! Faltaba envolver esto en la función publicar
const publicar = async () => {
  isSubmitting.value = true
  mensaje.value = ''
  
  // 0. Sacamos las coordenadas antes de nada
  const coords = await obtenerCoordenadas(form.direccion_texto)
  if (coords) {
    form.latitud = coords.lat
    form.longitud = coords.lon
  }

  // 1. Creamos el evento
  const eventoCreado = await mainStore.publicarEvento(form)

  if (eventoCreado && eventoCreado.id_evento) {
    console.log(`✅ Mercadillo creado. ID: ${eventoCreado.id_evento}`);
    console.log(`📸 Cantidad de fotos a subir: ${selectedFiles.value.length}`);
    
    // 2. Subimos las fotos (SI HAY ALGUNA)
    if (selectedFiles.value.length > 0) {
      mensaje.value = 'Subiendo las fotos... ⏳'
      tipoMensaje.value = 'success'
      
      // Llamamos a la función de subir imágenes
      await mainStore.subirImagenesEvento(eventoCreado.id_evento, selectedFiles.value)
      console.log("✅ Proceso de fotos terminado.");
    }

    mensaje.value = '¡Mercadillo publicado con éxito! 🎉'
    tipoMensaje.value = 'success'
  
    setTimeout(() => {
      emit('actualizar')
      emit('close')
    }, 1500)
  } else {
    mensaje.value = 'Error al obtener el ID del mercadillo.'
    tipoMensaje.value = 'error'
  }
  
  isSubmitting.value = false
}
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-content">
      
      <div class="modal-header">
        <h2>Nuevo Mercadillo</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <form @submit.prevent="publicar" class="modal-form">
        
        <div class="form-group">
          <label>NOMBRE DEL MERCADILLO</label>
          <input v-model="form.titulo" type="text" placeholder="Ej. Rastro de los Domingos" required />
        </div>

        <div class="form-group">
          <label>CATEGORÍA</label>
          <select v-model="form.id_categoria" required>
            <option value="" disabled selected>Selecciona una categoría</option>
            <option v-for="cat in mainStore.categorias" :key="cat.id_categoria" :value="cat.id_categoria">
              {{ cat.nombre }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>DIRECCIÓN</label>
          <input v-model="form.direccion_texto" type="text" placeholder="Ej. Calle Gran Vía, 12, Madrid" required />
          <small class="help-text">Pon la calle y la ciudad para que aparezca en el mapa.</small>
        </div>

        <div class="form-group">
          <label>FECHA DE INICIO</label>
          <input v-model="form.fecha_inicio" type="date" required />
        </div>
        <div class="form-group">
            <label>Fotos del Mercadillo (Puedes elegir varias)</label>
            <input 
              type="file" 
              accept="image/*" 
              multiple 
              @change="onFilesSelected" 
            />
            <small class="help-text" v-if="selectedFiles.length > 0">
              Has seleccionado {{ selectedFiles.length }} imagen(es).
            </small>
        </div>

        <div class="form-group">
          <label>DESCRIPCIÓN</label>
          <textarea 
            v-model="form.descripcion" 
            rows="3" 
            placeholder="Cuenta un poco qué se va a vender, si hay música, etc."
            style="width: 100%; padding: 12px 15px; border: 2px solid #eee; border-radius: 10px; font-family: inherit; resize: vertical;"
            required
          ></textarea>
        </div>

        <div v-if="mensaje" class="status-msg" :class="tipoMensaje">
          {{ mensaje }}
        </div>

        <button type="submit" class="btn-submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Buscando coordenadas y publicando...' : 'Publicar ahora' }}
        </button>

      </form>
    </div>
  </div>
</template>