<script setup>
import { onMounted, onUnmounted, watch, markRaw, nextTick } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../css/MapaInteractivo.css';

import { CATEGORIAS_MEC } from '../constants/mercadillos';

import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconShadowUrl from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: iconUrl,
  shadowUrl: iconShadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34]
});
L.Marker.prototype.options.icon = DefaultIcon;

const props = defineProps({
  eventos: {
    type: Array,
    default: () => []
  }
});

let map = null;
let markerLayer = null; 

const actualizarMarcadores = (listaEventos) => {
  if (!map || !markerLayer) return;

  markerLayer.clearLayers();

  if (listaEventos && listaEventos.length > 0) {
    const bounds = [];
    listaEventos.forEach(evento => {
      if (evento.latitud && evento.longitud) {
        const lat = parseFloat(evento.latitud);
        const lng = parseFloat(evento.longitud);

        if (!isNaN(lat) && !isNaN(lng)) {
          const posicion = [lat, lng];
          bounds.push(posicion);

          const infoCat = (CATEGORIAS_MEC && CATEGORIAS_MEC[evento.id_categoria]) 
                          ? CATEGORIAS_MEC[evento.id_categoria] 
                          : { color: '#E10818', nombre: 'Mercadillo' };

          const tituloEvento = evento.titulo || 'Mercadillo';
          const direccion = evento.direccion_texto || 'Dirección no especificada';
          
          let fechaTexto = '';
          if (evento.fecha_inicio) {
            const fechaObj = new Date(evento.fecha_inicio);
            fechaTexto = `<small class="popup-date">📅 ${fechaObj.toLocaleDateString()}</small><br>`;
          }

          const marker = L.marker(posicion)
            .bindPopup(`
              <div class="custom-popup">
                <strong class="popup-title" style="color: ${infoCat.color};">${tituloEvento}</strong><br>
                ${fechaTexto}
                <small class="popup-address">📍 ${direccion}</small>
              </div>
            `);
          
          markerLayer.addLayer(marker);
        }
      }
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 }); 
    }
  }
};

let resizeObserver = null;

onMounted(() => {
  map = markRaw(L.map('map-container').setView([40.4168, -3.7038], 12));
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  markerLayer = L.layerGroup().addTo(map);
  actualizarMarcadores(props.eventos);

  const mapDiv = document.getElementById('map-container');
  if (mapDiv) {
    resizeObserver = new ResizeObserver(() => map?.invalidateSize());
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