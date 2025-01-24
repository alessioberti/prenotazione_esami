<template>
  <div class="flex min-h-full flex-1 items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-sm space-y-10">
      <div>
        <img class="mx-auto h-10 w-auto" src="https://tailwindui.com/plus/img/logos/mark.svg?color=indigo&shade=600" alt="Your Company" />
        <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">Sign in to your account</h2>
      </div>
      <form class="space-y-6" @submit.prevent="handleLogin">
        <div>
          <div class="col-span-2">
            <input
                id="email"
                type="text"
                class="button-login"
                v-model="email"
                required
                placeholder="Inserisci la tua email"
              />
          </div>
          <div class="-mt-px">
            <input
                id="password"
                type="password"
                class="button-login"
                v-model="password"
                required
                placeholder="Inserisci la tua password"
              /></div>
        </div>


       

      

        <div>
          <button type="submit" class="button-submit-login"  :disabled="loading">Sign in</button>
        </div>
      </form>

      <div class="flex items-center justify-between">
          <div  class="font-semibold text-indigo-600 hover:text-indigo-500"> <router-link to="/register">Registrati</router-link></div>
          <div class="font-semibold text-indigo-600 hover:text-indigo-500"><router-link to="/reset-password">Recupera Password</router-link></div>
        </div>

       <!-- Messaggio di errore -->
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>



    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const email = ref('')
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
    await login(email.value, password.value)

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





