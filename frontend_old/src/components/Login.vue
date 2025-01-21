
<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Username" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from "../services/axios";

export default {
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post("/login", {
          username: this.username,
          password: this.password,
        });
        localStorage.setItem("token", response.data.access_token); // Salva il token
        this.$router.push("/new-booking"); // Naviga a NewBooking
      } catch (error) {
        this.errorMessage = "Credenziali errate o errore di login";
      }
    },
  },
};
</script>
