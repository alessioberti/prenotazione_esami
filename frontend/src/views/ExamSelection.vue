<template>
    <div class="exam-selection">
      <h2>Seleziona un Esame</h2>
      
      <select v-model="selectedExam" >
        <option disabled value="">-- Seleziona Esame --</option>
        <option 
          v-for="exam in examTypes" 
          :key="exam.exam_type_id" 
          :value="exam.exam_type_id"
        >
          {{ exam.name }}
        </option>
      </select>
  
      <!-- Data di partenza (opzionale) -->
      <label>Data di inizio</label>
      <input type="date" v-model="startDate" />
  
      <button 
        :disabled="!selectedExam" 
        @click="goToSlotsPage"
      >
        Avanti
      </button>
      <button @click="goBack">Indietro</button>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import api from '../composables/useApi'
  const router = useRouter()
  
  // Stato
  const examTypes = ref([])
  const selectedExam = ref('')
  const startDate = ref('2025-01-22') // valore di default
  
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
  