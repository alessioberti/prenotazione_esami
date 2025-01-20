<template>
  <div>
    <h2>Le tue prenotazioni</h2>
    <ul>
      <li v-for="booking in bookings" :key="booking.slot_id">
        Data: {{ booking.appointment_date }} - Ora: {{ booking.appointment_time_start }}
        <button @click="deleteBooking(booking.slot_id)">Cancella</button>
      </li>
    </ul>
    <button @click="$emit('go-back')">Torna indietro</button>
  </div>
</template>

<script>
import axios from "../services/axios";

export default {
  data() {
    return {
      bookings: [],
    };
  },
  async mounted() {
    await this.loadBookings();
  },
  methods: {
    async loadBookings() {
      try {
        const response = await axios.get("/slot_bookings", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        this.bookings = response.data;
      } catch (error) {
        alert("Errore nel caricamento delle prenotazioni");
      }
    },
    async deleteBooking(slotId) {
      try {
        await axios.delete(`/book_slot/${slotId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        alert("Prenotazione cancellata");
        this.loadBookings();
      } catch (error) {
        alert("Errore nella cancellazione della prenotazione");
      }
    },
  },
};
</script>