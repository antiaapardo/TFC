<script setup>
import { onMounted, onUnmounted, watch, markRaw } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../css/MapaInteractivo.css';

import { CATEGORIAS_MEC } from '../constants/mercadillos';

const router = useRouter(); 

const obtenerIconoPersonalizado = (colorHex) => {
  const svgHtml = `
    <svg width="32" height="42" viewBox="0 0 32 42" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0px 3px 4px rgba(0,0,0,0.3));">
      <path d="M16 0C7.16 0 0 7.16 0 16C0 27.6 14.2 40.8 14.8 41.4C15.4 42 16.6 42 17.2 41.4C17.8 40.8 32 27.6 32 16C32 7.16 24.8 0 16 0ZM16 22C12.68 22 10 19.32 10 16C10 12.68 12.68 10 16 10C19.32 10 22 12.68 22 16C22 19.32 19.32 22 16 22Z" fill="${colorHex}"/>
    </svg>
  `;

  return L.divIcon({
    html: svgHtml,
    className: 'custom-pin-container',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -40]
  });
};

const props = defineProps({
  eventos: {
    type: Array,
    default: () => []
  }
});

let map = null;
let markerLayer = null; 
let limitesActuales = []; 

const actualizarMarcadores = (listaEventos) => {
  if (!map || !markerLayer) return;

  markerLayer.clearLayers();
  limitesActuales = [];

  if (listaEventos && listaEventos.length > 0) {
    listaEventos.forEach(evento => {
      if (evento.latitud && evento.longitud) {
        const lat = parseFloat(evento.latitud);
        const lng = parseFloat(evento.longitud);

        if (!isNaN(lat) && !isNaN(lng)) {
          const posicion = [lat, lng];
          limitesActuales.push(posicion);

          const infoCat = (CATEGORIAS_MEC && CATEGORIAS_MEC[evento.id_categoria]) 
                          ? CATEGORIAS_MEC[evento.id_categoria] 
                          : { color: '#E10818', nombre: 'Mercadillo' };

          const tituloEvento = evento.titulo || 'Mercadillo';
          const direccion = evento.direccion_texto || 'Dirección no especificada';
          
          const idEvento = evento.event_id || evento.id_evento || evento.id;
          
          let fechaTexto = '';
          if (evento.fecha_inicio) {
            const fechaObj = new Date(evento.fecha_inicio);
            fechaTexto = `<small class="popup-date">📅 ${fechaObj.toLocaleDateString()}</small><br>`;
          }

          const marker = L.marker(posicion, {
            icon: obtenerIconoPersonalizado(infoCat.color)
          })
            .bindPopup(`
              <div class="custom-popup">
                <strong id="link-evento-${idEvento}" class="popup-title" style="color: ${infoCat.color}; cursor: pointer; text-decoration: underline;">
                  ${tituloEvento}
                </strong><br>
                ${fechaTexto}
                <small class="popup-address">📍 ${direccion}</small>
              </div>
            `);
          
          marker.on('popupopen', () => {
            const enlace = document.getElementById(`link-evento-${idEvento}`);
            if (enlace) {
              enlace.addEventListener('click', () => {
                router.push(`/evento/${idEvento}`); 
              });
            }
          });

          markerLayer.addLayer(marker);
        }
      }
    });

    if (limitesActuales.length > 0) {
      map.fitBounds(limitesActuales, { padding: [50, 50], maxZoom: 15 }); 
    }
  } else {
    map.setView([40.4168, -3.7038], 6);
  }
};

let resizeObserver = null;

onMounted(() => {
  map = markRaw(L.map('map-container').setView([40.4168, -3.7038], 6));
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  markerLayer = L.layerGroup().addTo(map);
  actualizarMarcadores(props.eventos);

  const mapDiv = document.getElementById('map-container');
  if (mapDiv) {
    resizeObserver = new ResizeObserver(() => {
      if (map) {
        map.invalidateSize();
        
        if (limitesActuales.length > 0) {
          setTimeout(() => {
            map.fitBounds(limitesActuales, { padding: [50, 50], maxZoom: 15 });
          }, 100);
        }
      }
    });
    resizeObserver.observe(mapDiv);
  }
});

onUnmounted(() => {
  resizeObserver?.disconnect();
  if (map) {
    map.remove();
    map = null;
  }
});

watch(() => props.eventos, (nuevosEventos) => {
  actualizarMarcadores(nuevosEventos);
}, { deep: true });
</script>

<template>
  <div id="map-container"></div>
</template>