import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import VerificarCuenta from '../views/VerificarCuenta.vue'

const routes = [
  {
    meta: {
      title: 'Panel Principal'
    },
    path: '/',
    name: 'home',
    component: Home
  },
  {
    meta: {
      title: 'Detalle del Evento'
    },
    path: '/evento/:id', 
    name: 'evento-detalle',
    component: () => import('../views/EventoDetalle.vue')
  },
  {
    meta: {
      title: 'Mis Favoritos'
    },
    path: '/favoritos', 
    name: 'favoritos',
    component: () => import('../views/Favoritos.vue')
  },
  {
    meta: {
      title: 'Perfil'
    },
    path: '/profile',
    name: 'profile',
    component: () => import('../views/Profile.vue')
  },
  {
    meta: {
      title: 'Login',
      fullScreen: true 
    },
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    meta: {
      title: 'Registro',
      fullScreen: true
    },
    path: '/verificar/:token',
    name: 'VerificarCuenta',
    component: () => import('../views/VerificarCuenta.vue')
  },
  {
    meta: { title: 'Editar Perfil' },
    path: '/profile/edit', 
    name: 'profile-edit',
    component: () => import('../views/EditarPerfil.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

export default router