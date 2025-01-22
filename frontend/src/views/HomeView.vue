<template>
    <div class="home-container">
      <h2>Sistema di prenotazione</h2>
      <button @click="goToBook">Prenota un Esame</button>
      <button @click="goToManage">Gestisci Prenotazioni</button>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  
  const router = useRouter()
  const { logout } = useAuth()
  
  const goToBook = () => {
    router.push({ name: 'book' })
  }
  
  const goToManage = () => {
    router.push({ name: 'manage' })
  }
  
  </script>
  
  <style scoped>
  .home-container {
    text-align: center;
    margin-top: 50px;
  }
  </style>
  