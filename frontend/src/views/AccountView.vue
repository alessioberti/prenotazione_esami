<template>
  <div class="account-management-container">
    <h2>Gestione Account</h2>

    <div class="account-field" v-for="(field, key) in fields" :key="key">
      <label :for="key">{{ field.label }}</label>
      <div class="field-wrapper">
        <span v-if="!field.editing">{{ field.value }}</span>
        <input
          v-else
          :id="key"
          :type="field.type"
          v-model="fields[key].value"
          :placeholder="field.placeholder"
        />
        <button @click="toggleEdit(key)">
          {{ field.editing ? 'Salva' : 'Modifica' }}
        </button>
      </div>
    </div>

    <!-- Sezione per cancellare account -->
    <div class="delete-account">
      <h3>Elimina Account</h3>
      <p>Attenzione: questa azione non può essere annullata.</p>
      <button @click="handleDelete" :disabled="loadingDelete" class="delete-btn">Elimina Account</button>
    </div>

    <!-- Messaggi di errore o successo -->
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../composables/useApi'
import { useRouter } from 'vue-router'

const router = useRouter()

// Campi dell'utente
const fields = ref({
  username: {
    label: 'Username',
    value: '',
    editing: false,
    type: 'text',
    placeholder: 'Aggiorna username',
  },
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
})

// Variabili reattive per stato e messaggi
const error = ref(null)
const message = ref(null)
const loadingDelete = ref(false)

// Funzione per abilitare/disabilitare modifica
const toggleEdit = async (key) => {
  const field = fields.value[key]
  if (field.editing) {
    // Salva modifiche
    try {
      error.value = null
      message.value = null

      await api.put('/account/update', {
        [key]: field.value,
      })

      message.value = `${field.label} aggiornato con successo!`
    } catch (err) {
      error.value = err?.response?.data?.error || `Errore durante l'aggiornamento di ${field.label}`
    }
  }
  field.editing = !field.editing
}

// Funzione per gestire l'eliminazione dell'account
const handleDelete = async () => {
  if (!confirm('Sei sicuro di voler eliminare il tuo account? Questa azione è irreversibile.')) return

  try {
    error.value = null
    message.value = null
    loadingDelete.value = true

    await api.delete('/account/delete')

    message.value = 'Account eliminato con successo.'
    router.push('/register')
  } catch (err) {
    error.value = err?.response?.data?.error || "Errore durante l'eliminazione dell'account"
  } finally {
    loadingDelete.value = false
  }
}

// Carica i dati attuali dell'utente
const loadUserData = async () => {
  try {
    const response = await api.get('/mylogin')
    const userData = response.data

    fields.value.username.value = userData.username
    fields.value.email.value = userData.email
    fields.value.telNumber.value = userData.tel_number
    fields.value.firstName.value = userData.first_name
    fields.value.lastName.value = userData.last_name
  } catch (err) {
    error.value = 'Errore nel caricamento dei dati utente'
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.account-management-container {
  width: 400px;
  margin: 50px auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.account-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
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
  padding: 5px 10px;
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

.delete-btn {
  background-color: #f44336;
}

.error {
  color: red;
  font-size: 0.9em;
}

.success {
  color: green;
  font-size: 0.9em;
}

.delete-account {
  text-align: center;
  margin-top: 20px;
}
</style>
