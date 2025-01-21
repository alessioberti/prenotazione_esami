<template>
    <div class="dashboard-container">
      <h2>Benvenuto nella Dashboard</h2>
  
      <button @click="goToBook">Prenota un Esame</button>
      <button @click="goToManage">Gestisci Prenotazioni</button>
      <button @click="handleLogout">Logout</button>
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
  
  const handleLogout = () => {
    // Chiamata eventuale a /logout sul backend
    // await api.post('/logout') ...
    logout() // rimuove token da localStorage
    router.push({ name: 'login' })
  }
  </script>
  
  <style scoped>
  .dashboard-container {
    text-align: center;
    margin-top: 50px;
  }
  </style>
  