<template>
  <v-container>
    <h2 class="text-h5 mb-4">Prenota un Esame</h2>

    <!-- Selezione del tipo di esame -->
    <v-select
      v-model="selectedExamType"
      :items="examTypes"
      label="Seleziona il tipo di esame"
      item-text="name"
      item-value="exam_type_id"
      outlined
      dense
      class="mb-4"
      @change="loadSlots"
    ></v-select>

    <!-- Filtri dinamici -->
    <div class="d-flex align-center mb-4">
      <v-select
        v-model="selectedLaboratory"
        :items="laboratories"
        label="Seleziona laboratorio"
        item-text="name"
        item-value="laboratory_id"
        outlined
        dense
        class="mr-4"
        @change="filterOperators"
      ></v-select>

      <v-select
        v-model="selectedOperator"
        :items="filteredOperators"
        label="Seleziona operatore"
        item-text="name"
        item-value="operator_id"
        outlined
        dense
        @change="filterSlots"
      ></v-select>
    </div>

    <!-- Messaggio informativo -->
    <v-alert type="info" border="left" color="blue" elevation="2" class="mb-4">
      Stai visualizzando le disponibilità di questa prestazione da <strong>{{ startDate }}</strong> a
      <strong>{{ endDate }}</strong>.
    </v-alert>

    <!-- Tabella delle disponibilità -->
    <div>
      <h3 class="text-h6 mb-2">Disponibilità Giornaliera</h3>
      <v-row>
        <v-col
          v-for="(day, index) in uniqueDays"
          :key="index"
          cols="12"
          md="4"
          class="d-flex"
        >
          <v-card
            class="pa-2 d-flex justify-space-between"
            elevation="2"
            outlined
            color="grey lighten-3"
          >
            <div>
              <v-icon color="red" class="mr-2">mdi-calendar</v-icon>
              <strong>{{ day }}</strong>
              <div v-for="location in availableLocations[day]" :key="location" class="text-caption">
                {{ location }}
              </div>
            </div>
            <v-btn color="primary" @click="selectDay(day)">Seleziona</v-btn>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

---

### **Script**
```javascript
<script>
import axios from "../services/axios";

export default {
  data() {
    return {
      selectedExamType: null,
      examTypes: [],
      laboratories: [],
      operators: [],
      filteredOperators: [],
      availableLocations: {},
      uniqueDays: [],
      selectedLaboratory: null,
      selectedOperator: null,
      startDate: "22 gennaio 2025",
      endDate: "21 febbraio 2025",
    };
  },
  async mounted() {
    await this.loadExamTypes();
    await this.loadLaboratories();
    await this.loadOperators();
  },
  methods: {
    async loadExamTypes() {
      const response = await axios.get("/exam_types");
      this.examTypes = response.data;
    },
    async loadLaboratories() {
      const response = await axios.get("/laboratories");
      this.laboratories = response.data;
    },
    async loadOperators() {
      const response = await axios.get("/operators");
      this.operators = response.data;
      this.filteredOperators = this.operators;
    },
    async loadSlots() {
      if (!this.selectedExamType) return;

      const response = await axios.get("/slots_availability", {
        params: { exam_type_id: this.selectedExamType },
      });

      const slots = response.data;

      // Genera giorni unici e location disponibili
      this.uniqueDays = [...new Set(slots.map((slot) => slot.operator_availability_date))];
      this.availableLocations = this.uniqueDays.reduce((acc, day) => {
        acc[day] = slots
          .filter((slot) => slot.operator_availability_date === day)
          .map((slot) => slot.location_name);
        return acc;
      }, {});
    },
    filterOperators() {
      // Filtra gli operatori in base al laboratorio selezionato
      if (this.selectedLaboratory) {
        this.filteredOperators = this.operators.filter(
          (op) => op.laboratory_id === this.selectedLaboratory
        );
      } else {
        this.filteredOperators = this.operators;
      }
      this.filterSlots();
    },
    filterSlots() {
      // Filtra gli slot in base ai filtri selezionati
      // (Non implementato completamente, aggiungilo secondo necessità)
    },
    selectDay(day) {
      alert(`Hai selezionato il giorno: ${day}`);
    },
  },
};
</script>
