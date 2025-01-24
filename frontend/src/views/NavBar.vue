<template>
  <nav class="flex justify-between items-center px-4 py-2 bg-gray-800 text-white">
    <router-link to="/" class="font-bold text-xl">Logo</router-link>
    <ul class="flex list-none gap-4">
      <template v-if="isLoggedIn">
        <li>
          <router-link to="/" class="hover:underline">Home</router-link>
        </li>
        <li>
          <router-link to="/manage" class="hover:underline">Prenotazioni</router-link>
        </li>
        <li class="flex items-center gap-2">
          <router-link to="/account" class="hover:underline">Gestione Account</router-link>
        </li>
      </template>
      <template v-else>
        <li>
          <router-link to="/" class="hover:underline">Home</router-link>
        </li>
        <li>
          <router-link to="/login" class="hover:underline">Login</router-link>
        </li>
      </template>
    </ul>
  </nav>
</template>

<script setup>
import { useAuth } from '../composables/useAuth';

const { isLoggedIn, userInfo } = useAuth();
</script>

<style>
</style>