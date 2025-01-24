<template>
    <div class="max-w-[1200px] mx-auto px-8 pb-10">
      <form @submit.prevent="handleRegister" class="space-y-6">
        <div>
          <h2 class="text-3xl font-black pb-10">Registrazione</h2>
        </div>
        <div class="space-y-6">
          <div class="flex flex-wrap gap-6">
            <div class="w-full sm:w-1/2">
              <label for="firstName" class="block text-sm font-medium text-gray-900">Nome</label>
              <input
                id="firstName"
                type="text"
                v-model="first_name"
                required
                placeholder="Inserisci nome"
                class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
              />
            </div>
            <div class="w-full sm:w-1/2">
              <label for="lastName" class="block text-sm font-medium text-gray-900">Cognome</label>
              <input
                id="lastName"
                type="text"
                v-model="last_name"
                required
                placeholder="Inserisci cognome"
                class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
              />
            </div>
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-900">Email</label>
            <input
              id="email"
              type="email"
              v-model="email"
              required
              pattern="^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
              placeholder="Inserisci email"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-900">Password</label>
            <input
              id="password"
              type="password"
              v-model="password"
              required
              minlength="8"
              maxlength="32"
              pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,32}$"
              placeholder="da 8 a 32 caratteri (Az-09-!@#$%_&*)"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
            />
          </div>
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-900">Conferma Password</label>
            <input
              id="confirmPassword"
              type="password"
              v-model="confirmPassword"
              required
              minlength="8"
              maxlength="32"
              placeholder="Conferma la tua password"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
            />
            <p v-if="passwordMismatch" class="text-red-600 text-sm">Le password non corrispondono.</p>
          </div>
          <div>
            <label for="telNumber" class="block text-sm font-medium text-gray-900">Telefono</label>
            <input
              id="telNumber"
              type="text"
              v-model="telNumber"
              required
              pattern="^\+?\d{10,13}$"
              placeholder="Inserisci telefono (es. +391234567890)"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
            />
          </div>
          <div>
            <button
              :disabled="loading || passwordMismatch"
              type="submit"
              class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Registrati
            </button>
          </div>
        </div>
      </form>
      <p v-if="error" class="text-red-600 text-sm mt-4">{{ error }}</p>
      <p v-if="message" class="text-green-600 text-sm mt-4">{{ message }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import api from '../composables/useApi';
  
  const router = useRouter();
  
  const email = ref('');
  const password = ref('');
  const confirmPassword = ref('');
  const telNumber = ref('');
  const first_name = ref('');
  const last_name = ref('');
  
  const error = ref(null);
  const message = ref(null);
  const loading = ref(false);
  
  const passwordMismatch = computed(() => password.value !== confirmPassword.value);
  
  const handleRegister = async () => {
    if (passwordMismatch.value) return;
  
    try {
      error.value = null;
      message.value = null;
      loading.value = true;
  
      const response = await api.post('/register', {
        email: email.value,
        password: password.value,
        tel_number: telNumber.value,
        first_name: first_name.value,
        last_name: last_name.value,
      });
  
      message.value = response.data.message || 'Registrazione completata!';
  
      router.push('/login');
    } catch (err) {
      error.value = err?.response?.data?.error || 'Errore di registrazione';
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style>
  </style>
  