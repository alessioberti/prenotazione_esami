<template>
  <div class="login-container">
    <h2>Login</h2>

    <form @submit.prevent="handleLogin">
      <div>
        <label>Username</label>
        <input type="text" v-model="username" />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="password" />
      </div>
      <button type="submit">Accedi</button>
    </form>

    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import api from '../composables/useApi'

const username = ref('')
const password = ref('')
const errorMessage = ref(null)

const router = useRouter()
const { login } = useAuth()

const handleLogin = async () => {
  try {
    errorMessage.value = null
    // Invio credenziali
    await api.post('/login', { 
      username: username.value, 
      password: password.value 
    })

    await login()

    // Ora reindirizziamo
    router.push({ name: 'dashboard' })

  } catch (err) {
    console.error('Errore login:', err)
    errorMessage.value = err?.response?.data?.error || 'Errore di login'
  }
}
</script>
