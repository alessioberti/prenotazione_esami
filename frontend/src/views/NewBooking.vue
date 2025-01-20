<template>
    <div>
      <h2>Prenota un nuovo esame</h2>
      <div v-if="currentStep === 1">
        <h3>Step 1: Seleziona il tipo di esame</h3>
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
        <h3>Step 2: Seleziona operatore e laboratorio</h3>
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
        <button :disabled="!selectedOperator && !selectedLaboratory" @click="goToNextStep">Avanti</button>
      </div>
  
      <div v-if="currentStep === 3">
        <h3>Step 3: Slot disponibili</h3>
        <div v-if="loading">Caricamento...</div>
        <ul v-if="slots.length > 0">
          <li v-for="slot in slots" :key="slot.operator_availability_id">
            Operatore: {{ slot.operator_name }} - Tipo di esame: {{ slot.exam_type_name }} -
            Data: {{ slot.operator_availability_date }} - Orario: {{ slot.operator_availability_slot_start }} -
            {{ slot.operator_availability_slot_end }}
            <button @click="bookSlot(slot)">Prenota</button>
          </li>
        </ul>
        <div v-else-if="!loading && slots.length === 0">Nessun slot disponibile</div>
        <button @click="goToPreviousStep">Indietro</button>
      </div>
  
      <div v-if="currentStep === 4">
        <h3>Step 4: Conferma Prenotazione</h3>
        <p><strong>Operatore:</strong> {{ selectedSlot.operator_name }}</p>
        <p><strong>Tipo di esame:</strong> {{ selectedSlot.exam_type_name }}</p>
        <p><strong>Data:</strong> {{ selectedSlot.operator_availability_date }}</p>
        <p><strong>Orario:</strong> {{ selectedSlot.operator_availability_slot_start }} - {{ selectedSlot.operator_availability_slot_end }}</p>
        <button @click="goToPreviousStep">Indietro</button>
        <button @click="confirmBooking">Conferma</button>
      </div>
  
      <button v-if="currentStep > 1" @click="$emit('go-back')">Torna al menu</button>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        currentStep: 1,
        examTypes: [],
        laboratories: [],
        operators: [],
        slots: [],
        selectedExamType: null,
        selectedLaboratory: null,
        selectedOperator: null,
        selectedSlot: null,
        loading: false,
      };
    },
    methods: {
      async fetchExamTypes() {
        try {
          const response = await axios.get("/exam_types", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
          });
          this.examTypes = response.data;
        } catch (error) {
          console.error("Errore nel caricamento dei tipi di esame:", error);
        }
      },
      async fetchLaboratoriesAndOperators() {
        this.loading = true;
        try {
          const [labsResponse, opsResponse] = await Promise.all([
            axios.get("/laboratories", {
              params: { exam_id: this.selectedExamType },
              headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            }),
            axios.get("/operators", {
              params: { exam_id: this.selectedExamType },
              headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            }),
          ]);
          this.laboratories = labsResponse.data;
          this.operators = opsResponse.data;
        } catch (error) {
          console.error("Errore nel caricamento di laboratori e operatori:", error);
        } finally {
          this.loading = false;
        }
      },
      async fetchSlots() {
        this.loading = true;
        try {
          const response = await axios.get("/slots_availability", {
            params: {
              exam_type_id: this.selectedExamType,
              laboratory_id: this.selectedLaboratory || undefined,
              operator_id: this.selectedOperator || undefined,
            },
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
          });
          this.slots = response.data;
        } catch (error) {
          console.error("Errore nel caricamento degli slot:", error);
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
      bookSlot(slot) {
        this.selectedSlot = slot;
        this.currentStep = 4;
      },
      async confirmBooking() {
        try {
          await axios.post(
            "/book_slot",
            { slot_id: this.selectedSlot.operator_availability_id },
            {
              headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            }
          );
          alert("Prenotazione confermata!");
          this.currentStep = 1; // Torna all'inizio
        } catch (error) {
          console.error("Errore nella conferma della prenotazione:", error);
          alert("Errore nella prenotazione");
        }
      },
    },
    mounted() {
      this.fetchExamTypes();
    },
  };
  </script>
  