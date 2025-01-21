<template>
    <div>
      <h1>Login</h1>
      <form @submit.prevent="login">
        <input type="text" v-model="username" placeholder="Username" required />
        <input type="password" v-model="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      <p>
        <a href="#" @click.prevent="changePassword">Cambia Password</a> | 
        <a href="#" @click.prevent="register">Registrati</a>
      </p>
    </div>
  </template>
  
  <script>
  import { ref } from "vue";
  import axios from "../services/axios";
  
  export default {
    setup() {
      const username = ref("");
      const password = ref("");
  
      const login = async () => {
        try {
          const response = await axios.post("/login", {
            username: username.value,
            password: password.value,
          });
          localStorage.setItem("token", response.data.token);
          window.location.href = "/home";
        } catch (error) {
          console.error(error);
          alert("Credenziali errate, riprova.");
        }
      };
  
      const changePassword = () => {
        alert("Funzionalità di cambio password non implementata.");
      };
  
      const register = () => {
        alert("Funzionalità di registrazione non implementata.");
      };
  
      return { username, password, login, changePassword, register };
    },
  };
  </script>
  