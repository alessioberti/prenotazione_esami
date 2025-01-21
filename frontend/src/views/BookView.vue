<template>
  <div class="slots-page">
    <h2>Disponibilità Esame</h2>

    <!-- Filtri (operatore e laboratorio) -->
    <div class="filters">
      <label>Operatore:</label>
      <select v-model="selectedOperator" @change="onFilterChange">
        <option value="">-- Tutti --</option>
        <option 
          v-for="op in operators" 
          :key="op.operator_id" 
          :value="op.operator_id"
        >
          {{ op.name }}
        </option>
      </select>

      <label>Laboratorio:</label>
      <select v-model="selectedLaboratory" @change="onFilterChange">
        <option value="">-- Tutti --</option>
        <option 
          v-for="lab in labs" 
          :key="lab.laboratory_id" 
          :value="lab.laboratory_id"
        >
          {{ lab.name }}
        </option>
      </select>

      <!-- Data di inizio e fine (se non l’hai già selezionata nello step precedente) -->
      <label>Da:</label>
      <input type="date" v-model="fromDate" @change="onFilterChange"/>
      
      <label>A:</label>
      <input type="date" v-model="toDate" @change="onFilterChange"/>
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
          Orario: {{ slot.operator_availability_slot_start }} → {{ slot.operator_availability_slot_end }}
        </div>
        <button @click="bookSlot(slot)">Prenota</button>
      </div>
    </div>

    <!-- Paginazione -->
    <div class="pagination" v-if="totalPages > 1">
      <button @click="prevPage" :disabled="currentPage === 1">Prev</button>
      <span>Pagina {{ currentPage }} di {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../composables/useApi'

// Stato di questa pagina
const route = useRoute()

// Parametri passati dalla query
const examTypeId = ref(route.query.exam_type_id || '')
const fromDate = ref(route.query.date_from || '2025-01-22')
const toDate = ref('2025-02-21') // default, se non c’è in query

// Filtri operator e lab
const operators = ref([])
const selectedOperator = ref('')
const labs = ref([])
const selectedLaboratory = ref('')

// Slot totali (dopo la fetch)
const slots = ref([])

// Paginazione
const currentPage = ref(1)
const pageSize = 10 // numero di slot per pagina

// Caricamento filtri e slot all'avvio
onMounted(async () => {
  if (!examTypeId.value) {
    // Se manca l'examTypeId, reindirizza o mostra un errore
    console.error('Nessun exam_type_id specificato!')
    return
  }
  await fetchFilters() // operatori e lab per quell’esame
  await fetchSlots()
})

// 1. Carica operatori e laboratori in base all’esame
async function fetchFilters() {
  try {
    // Carica operatori
    const opResponse = await api.get('/operators', {
      params: {
        exam_id: examTypeId.value
      }
    })
    operators.value = opResponse.data

    // Carica lab
    const labResponse = await api.get('/laboratories', {
      params: {
        exam_id: examTypeId.value
      }
    })
    labs.value = labResponse.data
  } catch (err) {
    console.error('Errore caricamento filtri operator/lab:', err)
  }
}

// 2. Quando cambia un filtro, ricarichiamo gli slot
function onFilterChange() {
  // Se vuoi gestire filtri incrociati, potresti dover ricaricare
  // la lista operatori se si cambia lab e viceversa:
  // es: if (selectedOperator.value) { fetchLabs() } ...
  // Dipende dalla logica di business.
  currentPage.value = 1
  fetchSlots()
}

// 3. Fetch slot dal backend
async function fetchSlots() {
  try {
    // Esegui la chiamata con i parametri di filtraggio
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

// 4. Computed per la paginazione
const totalPages = computed(() => {
  if (!slots.value) return 1
  return Math.ceil(slots.value.length / pageSize)
})

// Questo array contiene solo gli slot della pagina corrente
const paginatedSlots = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize
  const endIndex = startIndex + pageSize
  return slots.value.slice(startIndex, endIndex)
})

// Metodi di navigazione pagina
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

// 5. Prenotazione dello slot
async function bookSlot(slot) {
  console.log('Prenoto slot:', slot)
  try {
    const response = await api.post('/book_slot', {
      availability_id: slot.operator_availability_id,
      operator_availability_date: slot.operator_availability_date,
      operator_availability_slot_start: slot.operator_availability_slot_start,
      operator_availability_slot_end: slot.operator_availability_slot_end
    })
    alert('Prenotazione riuscita')
  } catch (err) {
    console.error('Errore prenotazione slot:', err)
    alert('Errore nella prenotazione')
  }
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
}
</style>
