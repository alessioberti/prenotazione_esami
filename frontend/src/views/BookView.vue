<template>
    <div class="slots-page">
      <h2>Disponibilità Esame</h2>
  
      <!-- Sezione filtri -->
      <div class="filters">
        <!-- Filtro Operatore -->
        <label>Operatore:</label>
        <select v-model="selectedOperator">
          <option value="">-- Tutti --</option>
          <option
            v-for="op in operators"
            :key="op.operator_id"
            :value="op.operator_id"
          >
            {{ op.name }}
          </option>
        </select>
  
        <!-- Filtro Laboratorio -->
        <label>Laboratorio:</label>
        <select v-model="selectedLaboratory">
          <option value="">-- Tutti --</option>
          <option
            v-for="lab in labs"
            :key="lab.laboratory_id"
            :value="lab.laboratory_id"
          >
            {{ lab.name }}
          </option>
        </select>
  
        <!-- Filtro Date (data di inizio e fine) -->
        <label>Da:</label>
        <input type="date" v-model="fromDate" />
  
        <label>A:</label>
        <input type="date" v-model="toDate" />
  
        <!-- Bottone per applicare i filtri -->
        <button @click="applyFilters">Applica Filtri</button>
        <button @click="goBack">Indietro</button>
      </div>
  
      <hr />
  
      <!-- Visualizzazione slot -->
      <div v-if="paginatedSlots.length === 0">
        <p>Nessuno slot trovato.</p>
      </div>
      <div v-else>
        <div
          v-for="slot in paginatedSlots"
          :key="slot.operator_availability_slot_start"
          class="slot-item"
        >
          <div>
            <strong>{{ slot.operator_availability_date }}</strong>
            ({{ slot.operator_name }} - {{ slot.laboratory_name }})
          </div>
          <div>
            Orario:
            {{ slot.operator_availability_slot_start }}
            →
            {{ slot.operator_availability_slot_end }}
          </div>
          <button @click="openConfirmModal(slot)">Prenota</button>
        </div>
      </div>
  
      <!-- Paginazione -->
      <div class="pagination" v-if="totalPages > 1">
        <button @click="prevPage" :disabled="currentPage === 1">Prev</button>
        <span>Pagina {{ currentPage }} di {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
      </div>
  
      <!-- Modale di conferma prenotazione -->
      <div v-if="showConfirmModal" class="modal-overlay">
        <div class="modal-content">
          <h3>Conferma Prenotazione</h3>
          <p>
            <strong>Data:</strong>
            {{ selectedSlot?.operator_availability_date }}
          </p>
          <p>
            <strong>Orario:</strong>
            {{ selectedSlot?.operator_availability_slot_start }} →
            {{ selectedSlot?.operator_availability_slot_end }}
          </p>
          <p>
            <strong>Operatore:</strong> {{ selectedSlot?.operator_name }}<br />
            <strong>Laboratorio:</strong> {{ selectedSlot?.laboratory_name }}
          </p>
          <button @click="confirmBooking">Conferma</button>
          <button @click="cancelBooking">Annulla</button>
  
          <!-- Messaggio di errore -->
          <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
        </div>
      </div>
  
    </div>
</template>
  
<script setup>

    import { ref, onMounted, computed } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../composables/useApi' // import dell'istanza axios con baseURL e intercettori
    
    // Recuperiamo la route (contiene exam_type_id in querystring)
    const route = useRoute()
    const router = useRouter()

    // examTypeId può arrivare dalla rotta (es. /slots?exam_type_id=3)
    const examTypeId = ref(route.query.exam_type_id || '')
    
    // Filtri per operatori, laboratori, date
    const operators = ref([])
    const selectedOperator = ref('')
    const labs = ref([])
    const selectedLaboratory = ref('')
    const fromDate = ref(route.query.date_from || '2025-01-22')
    const toDate = ref('2025-02-21')
    
    // Array di slot e paginazione
    const slots = ref([])
    const currentPage = ref(1)
    const pageSize = 10
    
    // Variabili per la modale di conferma
    const showConfirmModal = ref(false)
    const selectedSlot = ref(null)
    const errorMessage = ref('') // per visualizzare eventuali errori
    
    
  


    // onMounted: carica i filtri base e gli slot
    onMounted(async () => {
      if (!examTypeId.value) {
        console.error('Nessun exam_type_id specificato!')
        // In caso volessi bloccare la pagina o reindirizzare altrove:
        // router.push({ name: 'someRoute' })
        return
      }
      await fetchFilters()
      await fetchSlots()
    })

    // Carica operatori e laboratori di base (filtrati solo per exam_type)
    async function fetchFilters() {
      try {
        const opResponse = await api.get('/operators', {
          params: {
            exam_id: examTypeId.value
          }
        })
        operators.value = opResponse.data
      
        const labResponse = await api.get('/laboratories', {
          params: {
            exam_id: examTypeId.value
          }
        })
        labs.value = labResponse.data
      } catch (err) {
        console.error('Errore caricamento filtri:', err)
      }
    }

    // Carica gli slot dal backend
    async function fetchSlots() {
      try {
        const response = await api.get('/slots_availability', {
          params: {
            exam_type_id: examTypeId.value,
            operator_id: selectedOperator.value || null,
            laboratory_id: selectedLaboratory.value || null,
            datetime_from_filter: fromDate.value,
            datetime_to_filter: toDate.value
          }
        })
        slots.value = response.data
      } catch (err) {
        console.error('Errore caricamento slots:', err)
        slots.value = []
      }
    }

    // Al click su "Applica Filtri"
    async function applyFilters() {
      currentPage.value = 1
      errorMessage.value = ''
      await fetchSlots()
    }

    // Paginazione
    const totalPages = computed(() => {
      if (!slots.value) return 1
      return Math.ceil(slots.value.length / pageSize)
    })

    const paginatedSlots = computed(() => {
      const startIndex = (currentPage.value - 1) * pageSize
      const endIndex = startIndex + pageSize
      return slots.value.slice(startIndex, endIndex)
    })

    function prevPage() {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    function nextPage() {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    function goBack() {
        router.back()
    }
    // Apertura modale di conferma
    function openConfirmModal(slot) {
      selectedSlot.value = slot
      showConfirmModal.value = true
      errorMessage.value = ''
    }

    // Conferma prenotazione (chiamata a /book_slot)
    // e se successo => reindirizza a /manage
    async function confirmBooking() {
      if (!selectedSlot.value) return
    
      errorMessage.value = ''
      try {
        await api.post('/book_slot', {
          availability_id: selectedSlot.value.operator_availability_id,
          operator_availability_date: selectedSlot.value.operator_availability_date,
          operator_availability_slot_start: selectedSlot.value.operator_availability_slot_start,
          operator_availability_slot_end: selectedSlot.value.operator_availability_slot_end,
          // puoi passare exam_type_id, se il tuo backend lo richiede espressamente
          exam_type_id: examTypeId.value
        })
        // Prenotazione effettuata con successo
        alert('Prenotazione avvenuta con successo!')
        // Chiudo la modale e resetto lo slot selezionato
        showConfirmModal.value = false
        selectedSlot.value = null
        // Reindirizza alla pagina /manage
        router.push({ name: 'manage' })
      } catch (err) {
        console.error('Errore prenotazione slot:', err)
        if (err.response?.status === 409) {
          // Errore specifico: utente ha già prenotato lo stesso esame
          errorMessage.value = 'Hai già prenotato questo esame!'
        } else {
          // Errore generico
          errorMessage.value = err.response?.data?.error || 'Errore durante la prenotazione'
        }
      }
    }

    // Annulla modale
    function cancelBooking() {
      showConfirmModal.value = false
      selectedSlot.value = null
      errorMessage.value = ''
    }
</script>    
<style scoped>
    .slots-page {
      width: 90%;
      max-width: 1000px;
      margin: 0 auto;
    }

    .filters {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }

    .slot-item {
      border: 1px solid #ccc;
      padding: 8px;
      margin: 6px 0;
    }

    .pagination {
      margin-top: 1rem;
      text-align: center;
    }

    /* Semplice stile per la modale di conferma */
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
    