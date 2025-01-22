<template>
  <div class="slots-page">
    <h2>Disponibilità Esame</h2>

    <!-- Sezione filtri -->
    <div class="filters">
      <label>Operatore:</label>
      <select v-model="selectedOperator">
        <option value="">-- Tutti --</option>
        <option v-for="op in operators" :key="op.operator_id" :value="op.operator_id">
          {{ op.name }}
        </option>
      </select>

      <label>Laboratorio:</label>
      <select v-model="selectedLaboratory">
        <option value="">-- Tutti --</option>
        <option v-for="lab in labs" :key="lab.laboratory_id" :value="lab.laboratory_id">
          {{ lab.name }}
        </option>
      </select>

      <label>Da:</label>
      <input type="date" v-model="fromDate" />

      <label>A:</label>
      <input type="date" v-model="toDate" />

      <button @click="applyFilters">Applica Filtri</button>
      <button @click="goBack">Indietro</button>
    </div>

    <hr />

    <!-- Visualizzazione slot -->
    <div v-if="paginatedSlots.length === 0">
      <p>Nessuno slot trovato.</p>
    </div>
    <div v-else>
      <div v-for="slot in paginatedSlots" :key="slot.operator_availability_slot_start" class="slot-item">
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
        <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../composables/useApi';

const route = useRoute();
const router = useRouter();

// Filtri e stato degli slot
const examTypeId = ref(route.query.exam_type_id || '');
const operators = ref([]);
const selectedOperator = ref('');
const labs = ref([]);
const selectedLaboratory = ref('');
const toDate = ref('');
const fromDate = ref(route.query.date_from || '');
const slots = ref([]);
const currentPage = ref(1);
const pageSize = 10;

// Variabili per modale e messaggi
const showConfirmModal = ref(false);
const selectedSlot = ref(null);
const errorMessage = ref('');

onMounted(async () => {
  if (!examTypeId.value) {
    console.error('Nessun exam_type_id specificato!');
    return;
  }
  await fetchFilters();
  await fetchSlots();
});

async function fetchFilters() {
  try {
    const opResponse = await api.get('/operators', { params: { exam_id: examTypeId.value } });
    operators.value = opResponse.data;

    const labResponse = await api.get('/laboratories', { params: { exam_id: examTypeId.value } });
    labs.value = labResponse.data;
  } catch (err) {
    console.error('Errore caricamento filtri:', err);
  }
}

async function fetchSlots() {
  try {
    const params = {
      exam_type_id: examTypeId.value,
      operator_id: selectedOperator.value || undefined,
      laboratory_id: selectedLaboratory.value || undefined,
      datetime_from_filter: fromDate.value || undefined,
      datetime_to_filter: toDate.value || undefined,
    };
    const response = await api.get('/slots_availability', { params });
    slots.value = response.data;
  } catch (err) {
    console.error('Errore caricamento slots:', err);
    slots.value = [];
    errorMessage.value = 'Errore durante il caricamento degli slot';
  }
}

function applyFilters() {
  currentPage.value = 1;
  fetchSlots();
}

const totalPages = computed(() => {
  if (!slots.value) return 1;
  return Math.ceil(slots.value.length / pageSize);
});

const paginatedSlots = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  return slots.value.slice(startIndex, endIndex);
});

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

function goBack() {
  router.back();
}

function openConfirmModal(slot) {
  selectedSlot.value = slot;
  showConfirmModal.value = true;
  errorMessage.value = '';
}

async function confirmBooking() {
  if (!selectedSlot.value) return;

  errorMessage.value = '';
  try {
    await api.post('/book_slot', {
      availability_id: selectedSlot.value.operator_availability_id,
      operator_availability_date: selectedSlot.value.operator_availability_date,
      operator_availability_slot_start: selectedSlot.value.operator_availability_slot_start,
      operator_availability_slot_end: selectedSlot.value.operator_availability_slot_end,
      exam_type_id: examTypeId.value,
    });

    alert('Prenotazione effettuata con successo!');
    showConfirmModal.value = false;
    selectedSlot.value = null;
    router.push({ name: 'manage' });
  } catch (err) {
    console.error('Errore prenotazione slot:', err);
    if (err.response?.status === 409) {
      errorMessage.value = 'Risulta una prenotazione attiva per questo esame';
    } else {
      errorMessage.value = err.response?.data?.error || 'Si è verificato un errore durante la prenotazione.';
    }
    await fetchSlots();
  }
}

function cancelBooking() {
  showConfirmModal.value = false;
  selectedSlot.value = null;
  errorMessage.value = '';
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
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
