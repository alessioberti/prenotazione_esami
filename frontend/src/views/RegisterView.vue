<template>
  <div class="container">

    <form @submit.prevent="handleRegister">
      <!-- Nome e Cognome in cima -->
      <div class="border-b border-gray-900/10 pb-4">
        <h2 class="text-primary text-3xl font-black ">Registrazione</h2>
      </div>
      <div class="gap-y-4 mt-4">
      
        <div class="flex justify-between gap-4 w-full">
      <div class="flex">
        <label for="firstName" class="label">Nome</label>
        <input
          id="firstName"
          type="text"
          v-model="first_name"
          required
          class="button-generic"
          placeholder="Inserisci nome"
        />
      </div>
      <div class="flex">
        <label for="lastName" class="label">Cognome</label>
        <input
          id="lastName"
          type="text"
          v-model="last_name"
          required
           class="button-generic"
          placeholder="Inserisci cognome"
        />
      </div>
    </div>
      <!-- Altri campi -->
      <div>
        <label for="username" class="label">Username</label>
        <input
          id="username"
          type="text"
          v-model="username"
          required
           class="button-generic"
          maxlength="30"
          pattern="^[0-9A-Za-z]{6,30}$"
          placeholder="Inserisci username"
        />
      </div>
      <div>
        <label for="email" class="label">Email</label>
        <input
          id="email"
          type="email"
          v-model="email"
          required
           class="button-generic"
          pattern="^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
          placeholder="Inserisci email"
        />
      </div>
      <div>
        <label for="password" class="label">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          required
           class="button-generic"
          minlength="8"
          maxlength="32"
          pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,32}$"
          placeholder="da 8 a 32 caratteri (Az-09-!@#$%_&*)"
        />
      </div>
      <div>
        <label for="confirmPassword" class="label">Conferma Password</label>
        <input
          id="confirmPassword"
          type="password"
          v-model="confirmPassword"
          required
           class="button-generic"
          minlength="8"
          maxlength="32"
          placeholder="Conferma la tua password"
        />
        <p v-if="passwordMismatch" class="error">Le password non corrispondono.</p>
      </div>
      <div>
        <label for="telNumber" class="label">Telefono</label>
        <input
          id="telNumber"
          type="text"
          v-model="telNumber"
           class="button-generic"
          required
          pattern="^\+?\d{10,13}$"
          placeholder="Inserisci telefono (es. +391234567890)"
        />
      </div>

      <!-- Pulsante di registrazione -->
      <button :disabled="loading || passwordMismatch" type="submit">Registrati</button>
    </div>
    </form>

    <!-- Messaggi di errore o successo -->
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../composables/useApi';

const router = useRouter();

// Variabili reattive per i campi del form
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const telNumber = ref('');
const first_name = ref('');
const last_name = ref('');

// Variabili reattive per stato e messaggi
const error = ref(null);
const message = ref(null);
const loading = ref(false); // Stato del pulsante

// Computed per verificare se le password corrispondono
const passwordMismatch = computed(() => password.value !== confirmPassword.value);

// Funzione per gestire la registrazione
const handleRegister = async () => {
  if (passwordMismatch.value) return; // Blocca se le password non corrispondono

  try {
    error.value = null;
    message.value = null;
    loading.value = true; // Disabilita il pulsante

    const response = await api.post('/register', {
      username: username.value,
      email: email.value,
      password: password.value,
      tel_number: telNumber.value,
      first_name: first_name.value,
      last_name: last_name.value,
    });

    // Messaggio di successo
    message.value = response.data.message || 'Registrazione completata!';

    // passa alla pagina di login
    router.push('/login');
  } catch (err) {
    // Messaggio di errore
    error.value = err?.response?.data?.error || 'Errore di registrazione';
  } finally {
    loading.value = false; // Riabilita il pulsante
  }
};
</script>

<style scoped>


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