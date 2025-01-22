<template>
  <div class="login-container">
    <h2>Login</h2>

    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          v-model="username"
          required
          placeholder="Inserisci il tuo username"
        />
      </div>
      <div>
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          required
          placeholder="Inserisci la tua password"
        />
      </div>
      <button type="submit" :disabled="loading">Accedi</button>
    </form>

    <!-- Messaggio di errore -->
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <!-- Collegamenti per registrazione e reset password -->
    <div class="links">
      <p>Non hai un account? <router-link to="/register">Registrati</router-link></p>
      <p>Hai dimenticato la password? <router-link to="/reset-password">Recupera Password</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const username = ref('')
const password = ref('')
const errorMessage = ref(null)
const loading = ref(false)

const router = useRouter()
const { login } = useAuth()

const handleLogin = async () => {
  try {
    errorMessage.value = null
    loading.value = true

    // Usa il composable per autenticarti
    await login(username.value, password.value)

    router.push({ name: 'home' })
  } catch (err) {
    console.error('Errore login:', err)
    errorMessage.value = err?.response?.data?.error || 'Errore di login'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
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

.links {
  text-align: center;
  font-size: 0.9em;
}
</style>
