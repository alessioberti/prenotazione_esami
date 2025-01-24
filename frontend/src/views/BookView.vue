<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '../composables/useApi';

// Stato del componente
const operators = ref([]);
const labs = ref([]);
const slots = ref([]);
const selectedOperatorId = ref('');
const selectedLaboratoryId = ref('');
const fromDate = ref('');
const toDate = ref('');
const currentPage = ref(1);
const pageSize = 10;
const showConfirmModal = ref(false);
const selectedSlot = ref(null);

// Ottieni l'id dell'esame dalla query string
const route = useRoute();
const examTypeId = ref(route.query.exam_type_id || '');

onMounted(async () => {
  await fetchSlotsAndFilters();
});

// Funzione per caricare gli slot e i filtri
async function fetchSlotsAndFilters() {
  try {
    const params = {
      exam_type_id: examTypeId.value,
      operator_id: selectedOperatorId.value || undefined,
      laboratory_id: selectedLaboratoryId.value || undefined,
      datetime_from_filter: fromDate.value || undefined,
      datetime_to_filter: toDate.value || undefined,
    };

    const response = await api.get('/slots_availability', { params });

    slots.value = response.data.slots || [];
    operators.value = response.data.operators || [];
    labs.value = response.data.laboratories || [];
  } catch (err) {
    console.error('Errore durante il caricamento dei dati:', err);
  }
}

// Funzioni per il modale
function openConfirmModal(slot) {
  selectedSlot.value = slot;
  showConfirmModal.value = true;
}

function closeConfirmModal() {
  selectedSlot.value = null;
  showConfirmModal.value = false;
}

async function confirmBooking() {
  if (!selectedSlot.value) return;

  try {
    // Preparazione dei parametri per la POST
    const data = {
      appointment_time_start: selectedSlot.value.operator_availability_slot_start,
      appointment_time_end: selectedSlot.value.operator_availability_slot_end,
      appointment_date: selectedSlot.value.operator_availability_date,
      availability_id: selectedSlot.value.operator_availability_id,
    };

    // Invio della richiesta POST
    await api.post('/book_slot', data);

    alert('Prenotazione confermata con successo!');
    closeConfirmModal();
  } catch (err) {
    console.error('Errore durante la prenotazione:', err);
    alert('Errore durante la prenotazione. Riprova.');
  }
}

// Applica i filtri
function applyFilters() {
  currentPage.value = 1;
  fetchSlotsAndFilters();
}

// Funzioni per la paginazione
const totalPages = computed(() => Math.ceil(slots.value.length / pageSize));
const paginatedSlots = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize;
  return slots.value.slice(startIndex, startIndex + pageSize);
});

function prevPage() {
  if (currentPage.value > 1) currentPage.value--;
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++;
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-3xl font-bold mb-6 text-center">Disponibilità Esame</h2>

    <!-- Filtri -->
    <div class="flex flex-wrap gap-4 mb-6">
      <div>
        <label for="operator" class="block text-lg font-medium text-gray-700">Operatore</label>
        <select
          id="operator"
          v-model="selectedOperatorId"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-lg"
          @change="applyFilters"
        >
          <option value="">-- Tutti --</option>
          <option v-for="operator in operators" :key="operator.id" :value="operator.id">
            {{ operator.name }}
          </option>
        </select>
      </div>

      <div>
        <label for="laboratory" class="block text-lg font-medium text-gray-700">Laboratorio</label>
        <select
          id="laboratory"
          v-model="selectedLaboratoryId"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-lg"
          @change="applyFilters"
        >
          <option value="">-- Tutti --</option>
          <option v-for="laboratory in labs" :key="laboratory.id" :value="laboratory.id">
            {{ laboratory.name }}
          </option>
        </select>
      </div>

      <div>
        <label for="fromDate" class="block text-lg font-medium text-gray-700">Da</label>
        <input
          id="fromDate"
          type="date"
          v-model="fromDate"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-lg"
          @change="applyFilters"
        />
      </div>

      <div>
        <label for="toDate" class="block text-lg font-medium text-gray-700">A</label>
        <input
          id="toDate"
          type="date"
          v-model="toDate"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-lg"
          @change="applyFilters"
        />
      </div>
    </div>

    <!-- Lista slot -->
    <div v-if="paginatedSlots.length === 0" class="text-center text-lg text-gray-500">Nessuno slot trovato.</div>
    <ul v-else role="list" class="divide-y divide-gray-200">
      <li
        v-for="slot in paginatedSlots"
        :key="slot.operator_availability_slot_start"
        @click="openConfirmModal(slot)"
        class="cursor-pointer py-4 px-6 flex justify-between hover:bg-gray-100 rounded-md"
      >
        <div>
          <p class="text-lg font-semibold text-gray-900">
            <strong class="mr-4">{{ slot.operator_availability_date }}</strong>
            {{ slot.operator_availability_slot_start }} → {{ slot.operator_availability_slot_end }}
          </p>
          <p class="mt-1 text-md text-gray-500">{{ slot.operator_name }}</p>
        </div>
        <div class="text-lg text-gray-700">
          {{ slot.laboratory_name }}
          <p class="text-md text-gray-500">{{ slot.laboratory_address }}</p>
        </div>
      </li>
    </ul>

    <!-- Modale di conferma -->
    <div
      v-if="showConfirmModal"
      class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50"
    >
      <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
        <h3 class="text-2xl font-semibold mb-4">Dettagli dello Slot</h3>
        <p class="text-lg"><strong>Data:</strong> {{ selectedSlot.operator_availability_date }}</p>
        <p class="text-lg">
          <strong>Orario:</strong> {{ selectedSlot.operator_availability_slot_start }} →
          {{ selectedSlot.operator_availability_slot_end }}
        </p>
        <p class="text-lg"><strong>Operatore:</strong> {{ selectedSlot.operator_name }}</p>
        <p class="text-lg"><strong>Laboratorio:</strong> {{ selectedSlot.laboratory_name }}</p>
        <p class="text-lg"><strong>Indirizzo:</strong> {{ selectedSlot.laboratory_address }}</p>

        <div class="mt-4 flex justify-end gap-4">
          <button
            @click="confirmBooking"
            class="px-4 py-2 text-lg font-semibold text-white bg-green-600 rounded-md hover:bg-green-500 focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Conferma Prenotazione
          </button>
          <button
            @click="closeConfirmModal"
            class="px-4 py-2 text-lg font-semibold text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300 focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
          >
            Chiudi
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
