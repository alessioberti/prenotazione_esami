<template>
    <div class="register-container">
      <h2>Registrazione</h2>
      <div>
        <label>Username</label>
        <input type="text" v-model="username" />
      </div>
      <div>
        <label>Email</label>
        <input type="email" v-model="email" />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="password" />
      </div>
      <div>
        <label>Telefono</label>
        <input type="text" v-model="telNumber" />
      </div>
      <div>
        <label>Nome</label>
        <input type="text" v-model="first_name" />
      </div>
      <div>
        <label>Cognome</label>
        <input type="text" v-model="last_name" />
      </div>
      <button @click="handleRegister">Registrati</button>
  
      <p v-if="error" style="color: red;">{{ error }}</p>
      <p v-if="message" style="color: green;">{{ message }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import api from '../composables/useApi' // la nostra istanza axios
  
  const username = ref('')
  const email = ref('')
  const password = ref('')
  const telNumber = ref('')
  const first_name = ref('')
  const last_name = ref('')
  const error = ref(null)
  const message = ref(null)
  
  const handleRegister = async () => {
    try {
      error.value = null
      message.value = null
  
      const response = await api.post('/register', {
        username: username.value,
        email: email.value,
        password: password.value,
        tel_number: telNumber.value,
        first_name: first_name.value,
        last_name: last_name.value
      })
  
      // se non ci sono errori, potresti informare l’utente che la registrazione è avvenuta
      message.value = response.data.message || 'Registrazione completata!'
    } catch (err) {
      error.value = err?.response?.data?.error || 'Errore di registrazione'
    }
  }
  </script>
  
  <style scoped>
  .register-container {
    width: 300px;
    margin: 50px auto;
  }
  </style>
  