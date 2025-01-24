<template>
  <div class="max-w-3xl mx-auto p-8 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Seleziona un Esame</h2>

    <!-- Lista degli esami -->
    <ul role="list" class="divide-y divide-gray-200">
      <li
        v-for="exam in examTypes"
        :key="exam.exam_type_id"
        @click="setSelectedExam(exam)"
        class="cursor-pointer py-4 px-6 flex justify-between hover:bg-gray-100 rounded-md"
      >
        <div>
          <p class="text-sm font-semibold text-gray-900">{{ exam.name }}</p>
          <p class="mt-1 text-xs text-gray-500">{{ exam.description }}</p>
        </div>
        <div class="text-sm text-gray-500">Clicca per selezionare</div>
      </li>
    </ul>

    <!-- Paginazione -->
    <div class="flex justify-between items-center mt-6">
      <button
        @click="prevPage"
        :disabled="offset === 0"
        class="px-4 py-2 text-sm font-semibold text-white bg-gray-600 rounded-md hover:bg-gray-500 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:bg-gray-300"
      >
        Precedente
      </button>
      <button
        @click="nextPage"
        :disabled="examTypes.length < limit"
        class="px-4 py-2 text-sm font-semibold text-white bg-gray-600 rounded-md hover:bg-gray-500 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:bg-gray-300"
      >
        Successivo
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import api from '../composables/useApi';
import { useRouter } from 'vue-router';

const router = useRouter();
const examTypes = ref([]);
const offset = ref(0);
const limit = ref(10);

const fetchExamTypes = async () => {
  try {
    const response = await api.get('/exam_types', {
      params: {
        offset: offset.value,
        limit: limit.value,
      },
    });
    examTypes.value = response.data;
  } catch (err) {
    console.error('Errore caricamento exam_types', err);
  }
};

const prevPage = () => {
  if (offset.value > 0) {
    offset.value -= limit.value;
    fetchExamTypes();
  }
};

const nextPage = () => {
  offset.value += limit.value;
  fetchExamTypes();
};

const setSelectedExam = (exam) => {
  router.push({
    name: 'slots',
    query: {
      exam_type_id: exam.exam_type_id,
    },
  });
};

onMounted(fetchExamTypes);
</script>

<style scoped>
/* Tutto gestito tramite TailwindCSS */
</style>
