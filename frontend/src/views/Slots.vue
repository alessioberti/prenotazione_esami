<template>
  <div>
    <h1>Gestione degli Slot</h1>
    <div v-if="currentStep === 1">
      <h2>Step 1: Seleziona il tipo di esame</h2>
      <label for="examTypes">Tipo di esame:</label>
      <select id="examTypes" v-model="selectedExamType">
        <option value="">Seleziona un tipo</option>
        <option v-for="exam in examTypes" :key="exam.exam_type_id" :value="exam.exam_type_id">
          {{ exam.name }}
        </option>
      </select>
      <button :disabled="!selectedExamType" @click="goToNextStep">Avanti</button>
    </div>

    <div v-if="currentStep === 2">
      <h2>Step 2: Seleziona operatore e laboratorio</h2>
      <div>
        <label for="operators">Operatore:</label>
        <select id="operators" v-model="selectedOperator">
          <option value="">Tutti</option>
          <option v-for="operator in operators" :key="operator.operator_id" :value="operator.operator_id">
            {{ operator.name }}
          </option>
        </select>
      </div>
      <div>
        <label for="laboratories">Laboratorio:</label>
        <select id="laboratories" v-model="selectedLaboratory">
          <option value="">Tutti</option>
          <option v-for="lab in laboratories" :key="lab.laboratory_id" :value="lab.laboratory_id">
            {{ lab.name }}
          </option>
        </select>
      </div>
      <button @click="goToPreviousStep">Indietro</button>
      <button :disabled="!selectedExamType" @click="goToNextStep">Avanti</button>
    </div>

    <div v-if="currentStep === 3">
      <h2>Step 3: Slot disponibili</h2>
      <div v-if="loading">Caricamento...</div>
      <ul v-if="slots.length > 0">
        <li v-for="slot in slots" :key="slot.operator_availability_id">
          Operatore: {{ slot.operator_name }} -
          Tipo di esame: {{ slot.exam_type_name }} -
          Data: {{ slot.operator_availability_date }} -
          Orario: {{ slot.operator_availability_slot_start }} -
          {{ slot.operator_availability_slot_end }}
        </li>
      </ul>
      <div v-else-if="!loading && slots.length === 0">Nessun slot disponibile</div>
      <button @click="goToPreviousStep">Indietro</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      token: '',
      examTypes: [],
      laboratories: [],
      operators: [],
      slots: [],
      selectedExamType: null,
      selectedLaboratory: null,
      selectedOperator: null,
      loading: false,
      currentStep: 1, 
    };
  },
  methods: {
    async fetchExamTypes() {
      try {
        const response = await axios.get('http://localhost:10000/exam_types', {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.examTypes = response.data;
      } catch (error) {
        console.error('Errore nel caricamento dei tipi di esame:', error);
      }
    },
    async fetchLaboratoriesAndOperators() {
      try {
        this.loading = true;
        const [labsResponse, opsResponse] = await Promise.all([
          axios.get('http://localhost:10000/laboratories', {
            params: { exam_id: this.selectedExamType },
            headers: { Authorization: `Bearer ${this.token}` },
          }),
          axios.get('http://localhost:10000/operators', {
            params: { exam_id: this.selectedExamType },
            headers: { Authorization: `Bearer ${this.token}` },
          }),
        ]);
        this.laboratories = labsResponse.data;
        this.operators = opsResponse.data;
      } catch (error) {
        console.error('Errore nel caricamento dei laboratori o degli operatori:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchSlots() {
      this.loading = true;
      try {
        const response = await axios.get('http://localhost:10000/slots_availability', {
          params: {
            exam_type_id: this.selectedExamType,
            laboratory_id: this.selectedLaboratory || undefined,
            operator_id: this.selectedOperator || undefined,
          },
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.slots = response.data;
      } catch (error) {
        console.error('Errore nel caricamento degli slot:', error);
      } finally {
        this.loading = false;
      }
    },
    goToNextStep() {
      if (this.currentStep === 1) {
        this.fetchLaboratoriesAndOperators();
      } else if (this.currentStep === 2) {
        this.fetchSlots();
      }
      this.currentStep++;
    },
    goToPreviousStep() {
      this.currentStep--;
    },
  },
  mounted() {
    this.token = localStorage.getItem('token');
    this.fetchExamTypes();
  },
};
</script>
