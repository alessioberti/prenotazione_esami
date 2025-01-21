<template>
    <div class="login-container">
      <h2>Login</h2>
      <div>
        <label>Username</label>
        <input type="text" v-model="username" />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="password" />
      </div>
      <button @click="handleLogin">Accedi</button>
  
      <p>
        Non hai un account?
        <router-link to="/register">Registrati</router-link>
      </p>
      <p>
        Hai dimenticato la password?
        <router-link to="/forgot">Recupera Password</router-link>
      </p>
  
      <p v-if="error" style="color: red;">{{ error }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  import api from '../composables/useApi' // la nostra istanza axios
  
  // Variabili reattive per i campi di input
  const username = ref('')
  const password = ref('')
  const error = ref(null)
  
  const router = useRouter()
  
  const { login } = useAuth()
  
  // funzione richiamata al click del bottone "Accedi"
  const handleLogin = async () => {
    try {
      error.value = null
      const response = await api.post('/login', {
        username: username.value,
        password: password.value
      })
      
      if (response.data.access_token) {
        // Salviamo il token
        login(response.data.access_token)
        // reindirizzo a /dashboard
        router.push({ name: 'dashboard' })
      }
    } catch (err) {
      console.error('Errore login:', err)
      // se la risposta è un errore, tipicamente potresti avere un response.status
      error.value = err?.response?.data?.error || 'Errore di login'
    }
  }
  </script>
  
  <style scoped>
  .login-container {
    width: 300px;
    margin: 50px auto;
  }
  </style>
  