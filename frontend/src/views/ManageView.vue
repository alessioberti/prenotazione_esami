<template>
  <div class="manage-container">
    <h2>Le mie Prenotazioni</h2>

    <!-- Se c'è un messaggio di errore, lo mostriamo -->
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <!-- Se c'è un messaggio di successo -->
    <p v-if="successMessage" class="success">{{ successMessage }}</p>

    <!-- Se l'array bookings è vuoto -->
    <div v-if="bookings.length === 0">
      <p>Non hai ancora prenotazioni.</p>
    </div>
    <div v-else>
      <!-- Elenco (o tabella) delle prenotazioni -->
      <table class="booking-table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Orario</th>
            <th>Operatore</th>
            <th>Laboratorio</th>
            <th>Stato</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="booking in bookings" :key="booking.appointment_id">
            <td>{{ booking.appointment_date }}</td>
            <td>
              {{ booking.appointment_time_start }} → {{ booking.appointment_time_end }}
            </td>
            <td>{{ booking.operator_name }}</td>
            <td>{{ booking.laboratory_name }}</td>
            <td>
              <span v-if="booking.rejected">Cancellata</span>
              <span v-else>Attiva</span>
            </td>
            <td>
              <!-- Mostra bottone "Cancella" solo se non è già rejected -->
              <button 
                v-if="!booking.rejected"
                @click="openCancelModal(booking)"
              >
                Cancella
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modale di conferma annullamento -->
    <div v-if="showCancelModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Conferma Cancellazione</h3>
        <p>
          Vuoi davvero annullare la prenotazione del
          <strong>{{ bookingToCancel?.appointment_date }}</strong>
          dalle
          <strong>{{ bookingToCancel?.appointment_time_start }}</strong>
          alle
          <strong>{{ bookingToCancel?.appointment_time_end }}</strong>?
        </p>
        <button @click="cancelBookingConfirmed">Sì, Annulla</button>
        <button @click="closeCancelModal">No, Indietro</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../composables/useApi'

/**
 * Questo componente mostra le prenotazioni dell'utente loggato,
 * e consente di "cancellarle" (impostare rejected=true) chiamando:
 * PUT /book_slot/<appointment_id>/reject
 */

// Stato locale
const bookings = ref([])         // lista prenotazioni
const errorMessage = ref('')
const successMessage = ref('')

// Variabili per la modale di conferma cancellazione
const showCancelModal = ref(false)
const bookingToCancel = ref(null)

// Al montaggio, carichiamo la lista delle prenotazioni
onMounted(async () => {
  await fetchBookings()
})

/**
 * Recupera le prenotazioni dell'utente loggato
 * (supponendo il tuo backend abbia GET /slot_bookings)
 */
async function fetchBookings() {
  try {
    errorMessage.value = ''
    successMessage.value = ''
    const resp = await api.get('/slot_bookings')
    bookings.value = resp.data
  } catch (err) {
    console.error('Errore fetchBookings:', err)
    errorMessage.value = err.response?.data?.error || 'Errore durante il recupero delle prenotazioni.'
  }
}

/**
 * Apre la modale di conferma per annullare una prenotazione
 */
function openCancelModal(booking) {
  errorMessage.value = ''
  successMessage.value = ''
  bookingToCancel.value = booking
  showCancelModal.value = true
}

/**
 * Chiude la modale senza fare nulla
 */
function closeCancelModal() {
  showCancelModal.value = false
  bookingToCancel.value = null
}

/**
 * Conferma la cancellazione della prenotazione
 * (PUT /book_slot/<appointment_id>/reject)
 */
async function cancelBookingConfirmed() {
  if (!bookingToCancel.value) return

  try {
    errorMessage.value = ''
    successMessage.value = ''

    // Chiamata al tuo endpoint PUT
    await api.put(`/book_slot/${bookingToCancel.value.appointment_id}/reject`)

    // Chiudiamo la modale
    showCancelModal.value = false

    // Aggiorniamo lo stato localmente:
    bookingToCancel.value.rejected = true
    successMessage.value = 'Prenotazione annullata con successo.'

    // bookingToCancel.value = null
    // In alternativa, se preferisci ricaricare l'intera lista:
    // await fetchBookings()
  } catch (err) {
    console.error('Errore annullamento prenotazione:', err)
    errorMessage.value = err.response?.data?.error || 'Errore durante la cancellazione.'
  } finally {
    bookingToCancel.value = null
  }
}
</script>

<style scoped>
.manage-container {
  max-width: 800px;
  margin: 20px auto;
}

/* Tabella */
.booking-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.booking-table th, .booking-table td {
  border: 1px solid #ccc;
  padding: 8px;
}

/* Messaggi */
.error {
  color: red;
  margin-top: 1rem;
}
.success {
  color: green;
  margin-top: 1rem;
}

/* Modale semplice */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  max-width: 400px;
}
</style>
