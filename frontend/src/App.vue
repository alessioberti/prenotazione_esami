<template>
  <div>
    <h1>Gestione Esami</h1>
    <div v-if="!token">
      <Login @login-success="handleLoginSuccess" />
    </div>
    <div v-else>
      <div v-if="currentStep === 'menu'">
        <h2>Seleziona un'opzione</h2>
        <button @click="currentStep = 'newBooking'">Prenota un esame</button>
        <button @click="currentStep = 'manageBookings'">Gestisci prenotazioni</button>
        <button @click="handleLogout">Logout</button>
      </div>
      <div v-if="currentStep === 'newBooking'">
        <NewBooking @go-back="currentStep = 'menu'" />
      </div>
      <div v-if="currentStep === 'manageBookings'">
        <ManageBookings @go-back="currentStep = 'menu'" />
      </div>
    </div>
  </div>
</template>

<script>
import Login from "./Login.vue";
import NewBooking from "./NewBooking.vue";
import ManageBookings from "./ManageBookings.vue";

export default {
  components: {
    Login,
    NewBooking,
    ManageBookings,
  },
  data() {
    return {
      token: localStorage.getItem("token") || null,
      currentStep: "menu",
    };
  },
  methods: {
    handleLoginSuccess(token) {
      this.token = token;
      localStorage.setItem("token", token);
      this.currentStep = "menu";
    },
    handleLogout() {
      this.token = null;
      localStorage.removeItem("token");
      this.currentStep = "menu";
    },
  },
};
</script>
