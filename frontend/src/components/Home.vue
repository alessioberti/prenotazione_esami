<template>
    <div>
      <h1>Home</h1>
      <button @click="goToNewBooking">Nuova Prenotazione</button>
      <button @click="manageBookings">Gestisci Prenotazioni</button>
    </div>
  </template>
  
  <script>
  import { useRouter } from "vue-router";
  
  export default {
    setup() {
      const router = useRouter();
  
      const goToNewBooking = () => {
        router.push("/new-booking");
      };
  
      const manageBookings = () => {
        alert("Funzionalità non ancora implementata.");
      };
  
      return { goToNewBooking, manageBookings };
    },
  };
  </script>
  