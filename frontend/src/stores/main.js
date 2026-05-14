import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

const manageErrors = (functionName, error, callback, customMessage) => {
  let type = 'danger' 
  let message = ''

  if (customMessage) {
    message = customMessage
  } else if (error) {
    if (error.response && error.response.data && error.response.data.status) {
      message = error.response.data.status.msg
    } else if (error.response && error.response.data && error.response.data.message) {
      message = error.response.data.message
    } else if (error.response && error.response.status) {
      message = `Error del servidor: ${error.response.status}`
    } else {
      message = error.message || 'Respuesta de API desconocida'
    }
  }

  const params = { type: type, msg: message }
  console.error(`❌ [${functionName} Error]:`, message)
  
  if (callback) {
    callback(params)
  }
  return message
}

export const useMainStore = defineStore('main', {
  // ==========================================
  // STATE: El almacén de datos
  // ==========================================
  state: () => ({
    apiEndpoint: API_URL,
    currentUser: JSON.parse(localStorage.getItem('mec_user')) || null,
    lastError: null,
    lastWarning: null,
    isLoading: false,
    categorias: [],
    eventos: [],
    eventosFiltrados: [],
    favoritos: [],
    verSoloFavoritos: false,
  }),

  getters: {
    userId: (state) => (state.currentUser ? state.currentUser.id_usuario : null),
  },

  // ==========================================
  // ACTIONS: Funciones que "hacen cosas"
  // ==========================================
  actions: {
    // ==========================================
    // SISTEMA DE AUTENTICACIÓN (LOGIN/REGISTRO)
    // ==========================================
    async registrarUsuario(datosUsuario) {
      this.isLoading = true;
      this.lastError = null;
      try {
        const r = await axios.post(`${this.apiEndpoint}/register`, datosUsuario);
        if (r.data && r.data.success) {
          return true;
        }
        return false;
      } catch (error) {
        this.lastError = manageErrors('registrarUsuario', error);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async loginUsuario(email, password) {
      this.isLoading = true;
      this.lastError = null;
      try {
        const r = await axios.post(`${this.apiEndpoint}/login`, { email, password });
        if (r.data && r.data.success) {
          this.currentUser = r.data.data;
          localStorage.setItem('mec_user', JSON.stringify(this.currentUser));
          this.fetchFavoritos();
          return true;
        }
        return false;
      } catch (error) {
        this.lastError = manageErrors('loginUsuario', error);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async verificarCuentaStore(token) {
      this.isLoading = true;
      try {
        const response = await axios.get(`${this.apiEndpoint}/verificar/${token}`);
        if (response.data && response.data.success) {
          return { success: true, msg: response.data.status.msg };
        } else {
          return { success: false, msg: response.data.status.msg || "Error al verificar la cuenta." };
        }
      } catch (error) {
        const msg = (error.response && error.response.data && error.response.data.status) 
                    ? error.response.data.status.msg 
                    : "El enlace de verificación no es válido o ha caducado.";
        return { success: false, msg };
      } finally {
        this.isLoading = false;
      }
    },

    cerrarSesion() {
      this.currentUser = null;
      this.favoritos = [];
      localStorage.removeItem('mec_user');
    },

    // ==========================================
    // EVENTOS Y CATEGORÍAS
    // ==========================================
    async eliminarEvento(idEvento) {
      this.isLoading = true;
      this.lastError = null;
      try {
        const r = await axios.delete(`${this.apiEndpoint}/eventos/${idEvento}`);
        if (r.data && r.data.success) {
          await this.fetchEventos(); 
          return true;
        }
        return false;
      } catch (error) {
        this.lastError = manageErrors('eliminarEvento', error);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // Unificado a async/await
    async fetchCategorias(callback = null) {
      this.lastError = null;
      try {
        const r = await axios.get(`${this.apiEndpoint}/categorias`);
        if (r.data && r.data.success) {
          this.categorias = r.data.data;
          if (callback) callback({ type: 'success', msg: 'Categorías cargadas' });
        }
      } catch (error) {
        this.lastError = manageErrors('fetchCategorias', error, callback);
      }
    },

    // Unificado a async/await
    async fetchEventos(callback = null) {
      this.lastError = null;
      this.isLoading = true;
      try {
        const r = await axios.get(`${this.apiEndpoint}/eventos`);
        if (r.data && r.data.success) {
          this.eventos = r.data.data;
          this.eventosFiltrados = r.data.data;
          if (callback) callback({ type: 'success', msg: 'Eventos cargados' });
        }
      } catch (error) {
        this.lastError = manageErrors('fetchEventos', error, callback);
      } finally {
        this.isLoading = false;
      }
    },
async publicarEvento(eventoData, callback) {
      this.isLoading = true;
      this.lastError = null;
      try {
        // 1. Mandamos los datos a Flask
        const res = await axios.post(`${this.apiEndpoint}/eventos`, eventoData);
        
        // 2. Refrescamos la lista de eventos
        await this.fetchEventos(); 
        
        if (callback) callback({ type: 'success', msg: 'Mercadillo publicado con éxito' });
        
        // 3. ¡LA MAGIA! 
        // res.data.data es donde Python ha metido tu {"id_evento": X}
        return res.data.data; 
        
      } catch (error) {
        console.error("Error al publicar:", error);
        this.lastError = "No se pudo crear el mercadillo.";
        return null; 
      } finally {
        this.isLoading = false;
      }
    },
    async subirImagenesEvento(idEvento, files) {
      try {
        const formData = new FormData();
        
        // Recorremos el array y metemos todas las imágenes bajo el mismo nombre: 'imagenes'
        files.forEach(file => {
          formData.append('imagenes', file); 
        });

        const res = await axios.post(`${this.apiEndpoint}/eventos/${idEvento}/imagenes`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        return true;
      } catch (error) {
        console.error("Error subiendo las imágenes:", error);
        return false;
      }
    },

    // ==========================================
    // FAVORITOS
    // ==========================================
    async fetchFavoritos() {
      // Usamos el getter seguro
      const idUsuario = this.userId;
      if (!idUsuario) return;

      try {
        const r = await axios.get(`${this.apiEndpoint}/favoritos/${idUsuario}`);
        if (r.data && r.data.success) {
          this.favoritos = r.data.data;
        }
      } catch (error) {
        manageErrors('fetchFavoritos', error);
      }
    },

    async toggleFavorito(idEvento) {
      const idUsuario = this.userId;
      if (!idUsuario) return;

      const index = this.favoritos.findIndex(f => f.id_evento === idEvento);

      try {
        if (index > -1) {
          this.favoritos.splice(index, 1);
          await axios.delete(`${this.apiEndpoint}/favoritos`, { 
            data: { id_usuario: idUsuario, id_evento: idEvento } 
          });
        } else {
          this.favoritos.push({ id_evento: Number(idEvento) });
          await axios.post(`${this.apiEndpoint}/favoritos`, { 
            id_usuario: idUsuario, id_evento: idEvento 
          });
        }
      } catch (error) {
        manageErrors('toggleFavorito', error);
        this.fetchFavoritos();
      }
    },

   // ==========================================
    // PERFIL DE USUARIO
    // ==========================================
async actualizarPerfil(datos) {
      this.isLoading = true;
      this.lastError = null;
      try {
        await axios.put(`${this.apiEndpoint}/usuarios/${this.currentUser.id_usuario}`, datos);
        
        this.currentUser = { ...this.currentUser, ...datos }; 
        
        localStorage.setItem('mec_user', JSON.stringify(this.currentUser));
        return true;
      } catch (error) {
        this.lastError = manageErrors('actualizarPerfil', error);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

async subirAvatar(file) {
      this.isLoading = true;
      this.lastError = null;
      try {
        const formData = new FormData();
        formData.append('avatar', file); 

        const res = await axios.post(`${this.apiEndpoint}/usuarios/${this.currentUser.id_usuario}/avatar`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        const urlBase = res.data.data.foto_url; 
        const nuevaUrlConCacheBuster = `${urlBase}?t=${new Date().getTime()}`;
        
        this.currentUser.foto_url = nuevaUrlConCacheBuster;
        localStorage.setItem('mec_user', JSON.stringify(this.currentUser));
        
        return true;
      } catch (error) {
        this.lastError = manageErrors('subirAvatar', error);
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    async eliminarAvatar() {
      this.isLoading = true;
      this.lastError = null;
      try {
        // 1. Le decimos al backend que borre la foto de la base de datos
        await axios.delete(`${this.apiEndpoint}/usuarios/${this.currentUser.id_usuario}/avatar`);

        // 2. Borramos la foto de la memoria de Vue
        this.currentUser.foto_url = null;
        
        // 3. Actualizamos el LocalStorage para que no vuelva a aparecer al hacer F5
        localStorage.setItem('mec_user', JSON.stringify(this.currentUser));
        
        return true;
      } catch (error) {
        console.error("Error al eliminar el avatar:", error);
        this.lastError = "Error de conexión al eliminar la foto.";
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async cambiarPassword(datos) {
      this.isLoading = true;
      this.lastError = null;
      try {
        await axios.put(`${this.apiEndpoint}/usuarios/${this.currentUser.id_usuario}/password`, datos);
        return true;
      } catch (error) {
        this.lastError = manageErrors('cambiarPassword', error);
        return false;
      } finally {
        this.isLoading = false;
      }
    }
  } 
}) 