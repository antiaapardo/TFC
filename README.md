# MEC: Mercadillos en Casa 

## Descripción del Proyecto

**Mercadillos en Casa (MEC)** es una aplicación multiplataforma diseñada para digitalizar y centralizar el sector de los eventos de venta temporales, tales como vaciados de casas, rastros solidarios y mercados vintage en España. 

El proyecto resuelve el problema de la fragmentación de información en redes sociales, ofreciendo un punto de encuentro organizado donde los **organizadores** pueden autogestionar sus eventos (CRUD) y los **visitantes** pueden descubrirlos fácilmente mediante un sistema de filtros y un mapa interactivo con geolocalización en tiempo real.

* **Frontend:** Vue 3 (Composition API) + Pinia + Vite + Leaflet.js
* **Backend:** Python + Flask (API RESTful)
* **Base de Datos:** MariaDB

---

## Configuración Necesaria

Para que el proyecto funcione en un entorno local, es necesario configurar las variables de entorno que permitirán la comunicación entre el cliente, el servidor y la base de datos.

### 1. Variables del Backend
En la carpeta raíz del Backend, crea un archivo llamado `.env` basándote en el fichero `.env.example` e introduce tus credenciales locales:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña_aqui
DB_NAME=nombre_base_datos_mec