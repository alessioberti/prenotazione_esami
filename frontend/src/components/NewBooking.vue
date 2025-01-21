<template>
    <div>
      <h1>Nuova Prenotazione</h1>
      <div>
        <label>Tipo di esame:</label>
        <select v-model="selectedExamType" @change="loadFilters">
          <option v-for="exam in examTypes" :key="exam.exam_type_id" :value="exam.exam_type_id">
            {{ exam.name }}
          </option>
        </select>
        <label>Laboratorio:</label>
        <select v-model="selectedLaboratory" @change="loadOperators">
          <option value="">Tutti</option>
          <option v-for="lab in laboratories" :key="lab.laboratory_id" :value="lab.laboratory_id">
            {{ lab.name }}
          </option>
        </select>
        <label>Operatore:</label>
        <select v-model="selectedOperator">
          <option value="">Tutti</option>
          <option v-for="op in operators" :key="op.operator_id" :value="op.operator_id">
            {{ op.name }}
          </option>
        </select>
        <label>Data Inizio:</label>
        <input type="date" v-model="startDate" />
        <label>Data Fine:</label>
        <input type="date" v-model="endDate" />
      </div>
      <button @click="loadSlots">Cerca</button>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Ora</th>
            <th>Laboratorio</th>
            <th>Operatore</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="slot in slots" :key="slot.slot_id">
            <td>{{ slot.appointment_date }}</td>
            <td>{{ slot.appointment_time_start }}</td>
            <td>{{ slot.laboratory }}</td>
            <td>{{ slot.operator }}</td>
            <td><button @click="bookSlot(slot.slot_id)">Prenota</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import axios from "../services/axios";
  
  export default {
    setup() {
      const examTypes = ref([]);
      const laboratories = ref([]);
      const operators = ref([]);
      const slots = ref([]);
  
      const selectedExamType = ref("");
      const selectedLaboratory = ref("");
      const selectedOperator = ref("");
      const startDate = ref("");
      const endDate = ref("");
  
      const loadExamTypes = async () => {
        const response = await axios.get("/exam_types");
        examTypes.value = response.data;
      };
  
      const loadFilters = async () => {
        const response = await axios.get("/laboratories", {
          params: { exam_id: selectedExamType.value },
        });
        laboratories.value = response.data;
        operators.value = []; // Resetta gli operatori quando cambia il laboratorio
      };
  
      const loadOperators = async () => {
        const response = await axios.get("/operators", {
          params: {
            exam_id: selectedExamType.value,
            laboratory_id: selectedLaboratory.value,
          },
        });
        operators.value = response.data;
      };
  
      const loadSlots = async () => {
        const response = await axios.get("/slots_availability", {
          params: {
            exam_type_id: selectedExamType.value,
            operator_id: selectedOperator.value,
            laboratory_id: selectedLaboratory.value,
            datetime_from_filter: startDate.value,
            datetime_to_filter: endDate.value,
          },
        });
        slots.value = response.data;
      };
  
      const bookSlot = async (slotId) => {
        await axios.post(`/book_slot`, { slot_id: slotId });
        alert("Slot prenotato con successo!");
      };
  
      onMounted(() => {
        loadExamTypes();
      });
  
      return {
        examTypes,
        laboratories,
        operators,
        slots,
        selectedExamType,
        selectedLaboratory,
        selectedOperator,
        startDate,
        endDate,
        loadSlots,
        loadFilters,
        loadOperators,
        bookSlot,
      };
    },
  };
  </script>
  