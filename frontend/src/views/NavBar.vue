<template>
  <nav class="navbar">
    <router-link to="/" class="logo">Logo</router-link>
    <ul class="nav-links">
      <template v-if="isLoggedIn">
        <li><router-link to="/">Home</router-link></li>
        <li><router-link to="/manage">Prenotazioni</router-link></li>
        <li> {{ userInfo?.username }} <button @click="handleLogout" class="logout-btn">Logout</button></li>
      </template>
      <template v-else>
        <li><router-link to="/">Home</router-link></li>
        <li><router-link to="/login">Login</router-link></li>
      </template>
    </ul>
  </nav>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { isLoggedIn, userInfo, logout } = useAuth() 

const handleLogout = async () => {
  await logout()
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #333;
  color: white;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1rem;
}

.nav-links li {
  display: inline;
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.logout-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
}

.logo {
  font-weight: bold;
  font-size: 1.5rem;
}
</style>


