<template>
   <router-view /> 
</template>

<script setup>

import { useAuth } from './composables/useAuth'
import { onMounted } from 'vue'

const { checkAuth, authLoading } = useAuth()

onMounted(async () => {
  await checkAuth() // Esegui il controllo autenticazione al caricamento dell'app
})


</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
