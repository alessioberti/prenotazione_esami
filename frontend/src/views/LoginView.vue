<template>
  <div class="flex min-h-full items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-sm space-y-10">
      <div>
        <h2 class="text-center text-2xl font-bold tracking-tight text-gray-900">
          Sign in to your account
        </h2>
      </div>

      <form class="space-y-6" @submit.prevent="handleLogin">
        <div class="space-y-4">
          <div>
            <input
              id="email"
              type="text"
              class="block w-full rounded-md bg-white px-3 py-2 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
              v-model="email"
              required
              placeholder="Inserisci la tua email"
            />
          </div>
          <div>
            <input
              id="password"
              type="password"
              class="block w-full rounded-md bg-white px-3 py-2 text-base text-gray-900 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-2 focus:outline-indigo-600"
              v-model="password"
              required
              placeholder="Inserisci la tua password"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            :disabled="loading"
          >
            Sign in
          </button>
        </div>
      </form>

      <div class="flex items-center justify-between">
        <router-link
          to="/register"
          class="font-semibold text-indigo-600 hover:text-indigo-500"
        >
          Registrati
        </router-link>
        <router-link
          to="/reset-password"
          class="font-semibold text-indigo-600 hover:text-indigo-500"
        >
          Recupera Password
        </router-link>
      </div>

      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const email = ref('');
const password = ref('');
const errorMessage = ref(null);
const loading = ref(false);

const router = useRouter();
const { login } = useAuth();

const handleLogin = async () => {
  try {
    errorMessage.value = null;
    loading.value = true;

    await login(email.value, password.value);

    router.push({ name: 'home' });
  } catch (err) {
    console.error('Errore login:', err);
    errorMessage.value = err?.response?.data?.error || 'Errore di login';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>

</style>
