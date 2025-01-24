<template>
  <div class="max-w-5xl mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Disponibilità Esame</h2>

    <!-- Filtri -->
    <div class="flex flex-wrap gap-4 mb-6">
      <div>
        <label for="operator" class="block text-sm font-medium text-gray-700">Operatore</label>
        <select
          id="operator"
          v-model="selectedOperatorId"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          @change="applyFilters"
        >
          <option value="">-- Tutti --</option>
          <option v-for="operator in operators" :key="operator.id" :value="operator.id">
            {{ operator.name }}
          </option>
        </select>
      </div>

      <div>
        <label for="laboratory" class="block text-sm font-medium text-gray-700">Laboratorio</label>
        <select
          id="laboratory"
          v-model="selectedLaboratoryId"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          @change="applyFilters"
        >
          <option value="">-- Tutti --</option>
          <option v-for="laboratory in labs" :key="laboratory.id" :value="laboratory.id">
            {{ laboratory.name }}
          </option>
        </select>
      </div>

      <div>
        <label for="fromDate" class="block text-sm font-medium text-gray-700">Da</label>
        <input
          id="fromDate"
          type="date"
          v-model="fromDate"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          @change="applyFilters"
        />
      </div>

      <div>
        <label for="toDate" class="block text-sm font-medium text-gray-700">A</label>
        <input
          id="toDate"
          type="date"
          v-model="toDate"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          @change="applyFilters"
        />
      </div>
    </div>

    <!-- Lista slot -->
    <div v-if="paginatedSlots.length === 0" class="text-center text-gray-500">Nessuno slot trovato.</div>
    <ul v-else role="list" class="divide-y divide-gray-200">
      <li
        v-for="slot in paginatedSlots"
        :key="slot.operator_availability_slot_start"
        @click="openConfirmModal(slot)"
        class="cursor-pointer py-4 px-6 flex justify-between hover:bg-gray-100 rounded-md"
      >
        <div>
          <p class="text-sm font-semibold text-gray-900">
            <strong class="mr-4">{{ slot.operator_availability_date }}</strong>
            {{ slot.operator_availability_slot_start }} → {{ slot.operator_availability_slot_end }}
          </p>
          <p class="mt-1 text-xs text-gray-500">{{ slot.operator_name }}</p>
        </div>
        <div class="text-sm text-gray-500">{{ slot.laboratory_name }}</div>
      </li>
    </ul>

    <!-- Paginazione -->
    <div class="flex justify-between items-center mt-6" v-if="totalPages > 1">
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
        class="px-4 py-2 text-sm font-semibold text-white bg-gray-600 rounded-md hover:bg-gray-500 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:bg-gray-300"
      >
        Precedente
      </button>
      <span class="text-sm text-gray-600">Pagina {{ currentPage }} di {{ totalPages }}</span>
      <button
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="px-4 py-2 text-sm font-semibold text-white bg-gray-600 rounded-md hover:bg-gray-500 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:bg-gray-300"
      >
        Successivo
      </button>
    </div>
  </div>
</template>

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

// Ottieni l'id dell'esame dalla query string
const route = useRoute();
const examTypeId = ref(route.query.exam_type_id || '');

onMounted(async () => {
  await fetchSlotsAndFilters();
});

// Funzione per caricare gli slot e i filtri
async function fetchSlotsAndFilters() {
  console.log('Valore di examTypeId:', examTypeId.value);
  try {
    const params = {
      exam_type_id: examTypeId.value,
      operator_id: selectedOperatorId.value || undefined,
      laboratory_id: selectedLaboratoryId.value || undefined,
      datetime_from_filter: fromDate.value || undefined,
      datetime_to_filter: toDate.value || undefined,
    };

    const response = await api.get('/slots_availability', { params });

    // Popola gli slot
    slots.value = response.data.slots || [];

    // Popola gli operatori
    operators.value = response.data.operators || [];

    // Popola i laboratori
    labs.value = response.data.laboratories || [];
  } catch (err) {
    console.error('Errore durante il caricamento dei dati:', err);
    slots.value = [];
    operators.value = [];
    labs.value = [];
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

function openConfirmModal(slot) {
  console.log('Slot selezionato:', slot);
}
</script>

<style>
</style>
