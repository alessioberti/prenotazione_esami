<template>
  <div class="register-container">
    <h2>Registrazione</h2>

    <form @submit.prevent="handleRegister">
      <div>
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          v-model="username"
          required
          placeholder="Inserisci username"
        />
      </div>
      <div>
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          v-model="email"
          required
          placeholder="Inserisci email"
        />
      </div>
      <div>
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          required
          minlength="8"
          placeholder="Inserisci password"
        />
      </div>
      <div>
        <label for="telNumber">Telefono</label>
        <input
          id="telNumber"
          type="text"
          v-model="telNumber"
          required
          pattern="^\\+?\\d{10,13}$"
          placeholder="Inserisci numero di telefono"
        />
      </div>
      <div>
        <label for="firstName">Nome</label>
        <input
          id="firstName"
          type="text"
          v-model="first_name"
          required
          placeholder="Inserisci nome"
        />
      </div>
      <div>
        <label for="lastName">Cognome</label>
        <input
          id="lastName"
          type="text"
          v-model="last_name"
          required
          placeholder="Inserisci cognome"
        />
      </div>

      <!-- Pulsante di registrazione -->
      <button :disabled="loading" type="submit">Registrati</button>
    </form>

    <!-- Messaggi di errore o successo -->
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../composables/useApi' // Import axios instance

// Variabili reattive per i campi del form
const username = ref('')
const email = ref('')
const password = ref('')
const telNumber = ref('')
const first_name = ref('')
const last_name = ref('')

// Variabili reattive per stato e messaggi
const error = ref(null)
const message = ref(null)
const loading = ref(false) // Stato del pulsante

// Funzione per gestire la registrazione
const handleRegister = async () => {
  try {
    error.value = null
    message.value = null
    loading.value = true // Disabilita il pulsante

    const response = await api.post('/register', {
      username: username.value,
      email: email.value,
      password: password.value,
      tel_number: telNumber.value,
      first_name: first_name.value,
      last_name: last_name.value,
    })

    // Messaggio di successo
    message.value = response.data.message || 'Registrazione completata!'
    clearForm() // Resetta il form
  } catch (err) {
    // Messaggio di errore
    error.value = err?.response?.data?.error || 'Errore di registrazione'
  } finally {
    loading.value = false // Riabilita il pulsante
  }
}

// Funzione per resettare i campi del form
const clearForm = () => {
  username.value = ''
  email.value = ''
  password.value = ''
  telNumber.value = ''
  first_name.value = ''
  last_name.value = ''
}
</script>

<style scoped>
.register-container {
  width: 300px;
  margin: 50px auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

form div {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
}

input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  color: red;
  font-size: 0.9em;
}

.success {
  color: green;
  font-size: 0.9em;
}
</style>
