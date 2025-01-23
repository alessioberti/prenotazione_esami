<template>
  <div class="reset-container">
    <h2>Reset Password</h2>

    <form @submit.prevent="handleReset">
      <div>
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          v-model="email"
          required
          placeholder="Inserisci la tua email"
        />
      </div>
      <button type="submit" :disabled="loading">Recupera Password</button>
    </form>

    <!-- Messaggi -->
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success">{{ successMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../composables/useApi'

const email = ref('')
const errorMessage = ref(null)
const successMessage = ref(null)
const loading = ref(false)

const handleReset = async () => {
  try {
    errorMessage.value = null
    successMessage.value = null
    loading.value = true

    const response = await api.post('/reset-password', { email: email.value })

    successMessage.value = response.data.message || 'Email di recupero inviata!'
  } catch (err) {
    console.error('Errore reset password:', err)
    errorMessage.value = err?.response?.data?.error || 'Errore nel recupero password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-container {
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
