<template>
  <div>
    <div v-if="currentView === 'login'">
      <h2>Login</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="loginData.username" placeholder="Username" required />
        <input v-model="loginData.password" type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      <p v-if="loginError">{{ loginError }}</p>
      <button @click="currentView = 'register'">Registrati</button>
      <button @click="currentView = 'resetPassword'">Reset Password</button>
    </div>

    <div v-if="currentView === 'register'">
      <h2>Registrazione</h2>
      <form @submit.prevent="handleRegister">
        <input v-model="registerData.username" placeholder="Username" required />
        <input v-model="registerData.password" type="password" placeholder="Password" required />
        <input v-model="registerData.email" type="email" placeholder="Email" required />
        <button type="submit">Registrati</button>
      </form>
      <button @click="currentView = 'login'">Torna al Login</button>
    </div>

    <div v-if="currentView === 'resetPassword'">
      <h2>Reset Password</h2>
      <form @submit.prevent="handleResetPassword">
        <input v-model="resetEmail" type="email" placeholder="Email" required />
        <button type="submit">Invia Reset</button>
      </form>
      <button @click="currentView = 'login'">Torna al Login</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      currentView: "login",
      loginData: {
        username: "",
        password: "",
      },
      registerData: {
        username: "",
        password: "",
        email: "",
      },
      resetEmail: "",
      loginError: "",
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post("/login", this.loginData);
        this.$emit("login-success", response.data.access_token);
      } catch (error) {
        this.loginError = "Credenziali errate o account disabilitato";
      }
    },
    async handleRegister() {
      try {
        await axios.post("/register", this.registerData);
        alert("Registrazione completata. Ora puoi accedere.");
        this.currentView = "login";
      } catch (error) {
        alert("Errore nella registrazione");
      }
    },
    async handleResetPassword() {
      // Placeholder per la logica di reset password
      alert("Reset password inviato all'email.");
      this.currentView = "login";
    },
  },
};
</script>
