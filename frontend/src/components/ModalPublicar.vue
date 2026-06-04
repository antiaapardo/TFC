<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useMainStore } from '../stores/main'
import '../css/ModalPublicar.css'

const props = defineProps({
  eventoEditar: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'actualizar'])
const mainStore = useMainStore()

const isSubmitting = ref(false)
const mensaje = ref('')
const tipoMensaje = ref('')
const selectedFiles = ref([])

const esModoEdicion = computed(() => props.eventoEditar !== null)

const form = reactive({
  id_evento: null,
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

onMounted(() => {
  if (mainStore.categorias.length === 0) {
    mainStore.fetchCategorias()
  }

  if (props.eventoEditar) {
    let fechaFormateada = ''
    if (props.eventoEditar.fecha_inicio) {
      // Ajuste para extraer la fecha y la hora correctamente para el input datetime-local
      const dateObj = new Date(props.eventoEditar.fecha_inicio)
      const tzOffset = dateObj.getTimezoneOffset() * 60000; 
      const localISOTime = (new Date(dateObj.getTime() - tzOffset)).toISOString().slice(0, 16);
      fechaFormateada = localISOTime;
    }

    Object.assign(form, {
      id_evento: props.eventoEditar.id_evento,
      titulo: props.eventoEditar.titulo,
      id_categoria: props.eventoEditar.id_categoria,
      direccion_texto: props.eventoEditar.direccion_texto,
      fecha_inicio: fechaFormateada,
      descripcion: props.eventoEditar.descripcion || '',
      latitud: props.eventoEditar.latitud,
      longitud: props.eventoEditar.longitud
    })
  }
})

const onFilesSelected = (event) => {
  const files = Array.from(event.target.files)
  selectedFiles.value = files.filter(file => file.type.startsWith('image/'))
}

const obtenerCoordenadas = async (direccion) => {
  try {
    let queryBusqueda = `${direccion.trim()}, España`;
    console.log("🔍 Buscando en el mapa:", queryBusqueda);
    
    let url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryBusqueda)}&limit=1&countrycodes=es`;
    let respuesta = await fetch(url, { headers: { 'Accept-Language': 'es' }});
    let datos = await respuesta.json();
    
    if (datos && datos.length > 0) {
      return { lat: parseFloat(datos[0].lat), lon: parseFloat(datos[0].lon) };
    }

    const partes = direccion.split(',');
    
    if (partes.length > 1) {
      const ciudad = partes[partes.length - 1].trim();
      queryBusqueda = `${ciudad}, España`;
      console.log("🔍 Buscando ciudad:", queryBusqueda);
      
      url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryBusqueda)}&limit=1&countrycodes=es`;
      respuesta = await fetch(url, { headers: { 'Accept-Language': 'es' }});
      datos = await respuesta.json();
      
      if (datos && datos.length > 0) {
        return { lat: parseFloat(datos[0].lat), lon: parseFloat(datos[0].lon) };
      }
    }

  } catch (error) {
    console.error("❌ Error en la geocodificación:", error);
  }
  return null;
};

const publicar = async () => {
  isSubmitting.value = true
  mensaje.value = ''
  
  if (!esModoEdicion.value || form.direccion_texto !== props.eventoEditar?.direccion_texto) {
    const coords = await obtenerCoordenadas(form.direccion_texto)
    
    if (coords) {
      form.latitud = coords.lat
      form.longitud = coords.lon
    } else {
      mensaje.value = '❌ No encontramos esa dirección. Prueba a poner solo la ciudad (Ej: Vigo).'
      tipoMensaje.value = 'error'
      isSubmitting.value = false
      return; 
    }
  }

  let exito = false;
  let idEventoFinal = form.id_evento;

  if (esModoEdicion.value) {
    exito = await mainStore.editarEvento(form)
    if (!exito) {
      mensaje.value = mainStore.lastError || 'Hubo un problema al editar.'
      tipoMensaje.value = 'error'
      isSubmitting.value = false
      return;
    }
  } else {
    const eventoCreado = await mainStore.publicarEvento(form)
    if (eventoCreado && eventoCreado.id_evento) {
      exito = true;
      idEventoFinal = eventoCreado.id_evento;
    }
  }

  if (exito) {
    if (selectedFiles.value.length > 0) {
      mensaje.value = 'Subiendo las fotos... ⏳'
      tipoMensaje.value = 'success'
      await mainStore.subirImagenesEvento(idEventoFinal, selectedFiles.value)
    }

    mensaje.value = esModoEdicion.value ? '¡Cambios guardados! 🎉' : '¡Mercadillo publicado con éxito! 🎉'
    tipoMensaje.value = 'success'
  
    setTimeout(() => {
      emit('actualizar')
      emit('close')
    }, 1500)
  } else {
    mensaje.value = 'Error al procesar el mercadillo.'
    tipoMensaje.value = 'error'
  }
  
  isSubmitting.value = false
}
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-content">
      
      <div class="modal-header">
        <h2>{{ esModoEdicion ? 'Editar Mercadillo' : 'Nuevo Mercadillo' }}</h2>
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
          <input v-model="form.fecha_inicio" type="datetime-local" required />
        </div>
        
        <div class="form-group">
            <label>{{ esModoEdicion ? 'Añadir nuevas fotos (Opcional)' : 'Fotos del Mercadillo (Puedes elegir varias)' }}</label>
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
          <span v-if="isSubmitting">Procesando...</span>
          <span v-else>{{ esModoEdicion ? 'Guardar Cambios' : 'Publicar ahora' }}</span>
        </button>

      </form>
    </div>
  </div>
</template>