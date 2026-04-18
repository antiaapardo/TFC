<template>
  <div id="map-container"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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

const props = defineProps(['eventos']);
let map;

onMounted(() => {
  map = L.map('map-container').setView([40.4168, -3.7038], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
});

watch(() => props.eventos, (nuevosEventos) => {
  if (nuevosEventos.length > 0) {
    nuevosEventos.forEach(evento => {
      L.marker([evento.latitud, evento.longitud])
        .addTo(map)
        .bindPopup(`<b>${evento.titulo}</b><br>${evento.direccion_texto}`);
      
      map.setView([evento.latitud, evento.longitud], 15);
    });
  }
}, { deep: true });
</script>

<style scoped>
#map-container {
  height: 100%; 
  width: 100%;
  z-index: 1;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 12px;
  font-family: 'Nunito', sans-serif;
}

:deep(.leaflet-container) {
  font-family: 'Nunito', sans-serif;
}
</style>