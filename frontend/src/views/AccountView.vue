<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Gestione Account</h2>

    <div class="grid grid-cols-1 gap-6">
      <div v-for="(field, key) in fields" :key="key" v-if="key !== 'username'">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <label :for="key" class="block text-sm font-medium text-gray-700">{{ field.label }}</label>
            <span v-if="!field.editing" class="block mt-1 text-gray-900">{{ field.value }}</span>
            <input
              v-else
              :id="key"
              :type="field.type"
              v-model="fields[key].value"
              :placeholder="field.placeholder"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm mt-1"
            />
          </div>
          <button
            @click="toggleEdit(key)"
            class="button"
          >
            {{ field.editing ? 'Salva' : 'Modifica' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Sezione per cancellare account -->
    <div class="mt-8">      
      <button
        @click="handleDelete"
        :disabled="loadingDelete"
        class="red-button flex items-center justify-center w-full rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
      >
        Elimina Account
      </button>
      <p class="text-sm text-gray-600">Attenzione: questa azione non può essere annullata.</p>
    </div>

    <!-- Messaggi di errore o successo -->
    <p v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</p>
    <p v-if="message" class="mt-4 text-sm text-green-600">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../composables/useApi';
import { useRouter } from 'vue-router';

const router = useRouter();
const fields = ref({
  email: {
    label: 'Email',
    value: '',
    editing: false,
    type: 'email',
    placeholder: 'Aggiorna email',
  },
  telNumber: {
    label: 'Telefono',
    value: '',
    editing: false,
    type: 'text',
    placeholder: 'Aggiorna telefono',
  },
  firstName: {
    label: 'Nome',
    value: '',
    editing: false,
    type: 'text',
    placeholder: 'Aggiorna nome',
  },
  lastName: {
    label: 'Cognome',
    value: '',
    editing: false,
    type: 'text',
    placeholder: 'Aggiorna cognome',
  },
});

const error = ref(null);
const message = ref(null);
const loadingDelete = ref(false);

const toggleEdit = async (key) => {
  const field = fields.value[key];
  if (field.editing) {
    try {
      error.value = null;
      message.value = null;

      await api.put('/account/update', {
        [key]: field.value,
      });

      message.value = `${field.label} aggiornato con successo!`;
    } catch (err) {
      error.value = err?.response?.data?.error || `Errore durante l'aggiornamento di ${field.label}`;
    }
  }
  field.editing = !field.editing;
};

const handleDelete = async () => {
  if (!confirm('Sei sicuro di voler eliminare il tuo account? Questa azione è irreversibile.')) return;

  try {
    error.value = null;
    message.value = null;
    loadingDelete.value = true;

    await api.delete('/account/delete');

    message.value = 'Account eliminato con successo.';
    router.push('/register');
  } catch (err) {
    error.value = err?.response?.data?.error || 'Errore durante l\'eliminazione dell\'account';
  } finally {
    loadingDelete.value = false;
  }
};

const loadUserData = async () => {
  try {
    const response = await api.get('/mylogin');
    const userData = response.data;

    fields.value.email.value = userData.email;
    fields.value.telNumber.value = userData.tel_number;
    fields.value.firstName.value = userData.first_name;
    fields.value.lastName.value = userData.last_name;
  } catch (err) {
    error.value = 'Errore nel caricamento dei dati utente';
  }
};

onMounted(() => {
  loadUserData();
});
</script>

<style scoped>
</style>
