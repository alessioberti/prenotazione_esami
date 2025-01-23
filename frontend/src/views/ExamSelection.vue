<template>
    <div class="container">
      <h2 class="title-page">Seleziona un Esame</h2>

      <div class="fixed top-16 w-72">
   
  </div>
      
      <!-- <select v-model="selectedExam" >
        <option disabled value="">-- Seleziona Esame --</option>
        <option 
          v-for="exam in examTypes" 
          :key="exam.exam_type_id" 
          :value="exam.exam_type_id"
        >
          {{ exam.name }}
        </option>
      </select> -->
     
  
      <!-- Data di partenza (opzionale) -->
      <label>Data di inizio</label>
      
      <input type="date" v-model="startDate" />

      <ul role="list" class="divide-y divide-gray-100">
  <li @click="setSelectedExam(exam)" class="item-list"  v-for="exam in examTypes" 
          :key="exam.exam_type_id" 
          :value="exam.exam_type_id">
    <div class="flex min-w-0 gap-x-4">
        <div class="min-w-0 flex-auto">
        <p class="text-sm/6 font-semibold text-gray-900"> {{ exam.name }}</p>
        <p class="mt-1 truncate text-xs/5 text-gray-500">leslie.alexander@example.com</p>
      </div>
    </div>
    <div class="hidden shrink-0 sm:flex sm:flex-col sm:items-end">
      <p class="text-sm/6 text-gray-900">Co-Founder / CEO</p>
      <p class="mt-1 text-xs/5 text-gray-500">Last seen <time datetime="2023-01-23T13:23Z">3h ago</time></p>
    </div>
  </li>

</ul>


  
<div class="flex w-full justify-end pr-3 mt-4">
      <div class="button px-10 cursor-pointer" @click="goBack">Indietro</div></div>
    </div>
  </template>
  
  <script setup>
  
  import { onMounted, ref,computed } from 'vue'
  import {
  Combobox,
  ComboboxInput,
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
  TransitionRoot,
} from '@headlessui/vue'
  import { useRouter } from 'vue-router'
  import api from '../composables/useApi'
  const router = useRouter()
  const enabled = ref(false)



let query = ref('')

let filteredPeople = computed(() =>
  query.value === ''
    ? people
    : people.filter((person) =>
        person.name
          .toLowerCase()
          .replace(/\s+/g, '')
          .includes(query.value.toLowerCase().replace(/\s+/g, ''))
      )
)

  // Stato
  const examTypes = ref([])
  const selectedExam = ref('')
  const startDate = ref(new Date().toISOString().split('T')[0]);
  
  onMounted(fetchExamTypes)
  
  async function fetchExamTypes() {
    try {
      const response = await api.get('/exam_types')
      examTypes.value = response.data
    } catch (err) {
      console.error('Errore caricamento exam_types', err)
    }
  }
  
  // tasto indietro
  function goBack() {
    router.back()
  
  }

  function setSelectedExam(exam) {
    selectedExam.value = exam.exam_type_id

    router.push({
      name: 'slots',
      query: {
        exam_type_id: selectedExam.value,
        date_from: startDate.value
      }
    })
  }

  function goToSlotsPage() {
    // Passiamo examTypeId e startDate come query param (o param)
    router.push({
      name: 'slots',
      query: {
        exam_type_id: selectedExam.value,
        date_from: startDate.value
      }
    })
  }
  </script>
  
  <style scoped>
  .exam-selection {
    width: 400px;
    margin: 0 auto;
  }
  </style>
  