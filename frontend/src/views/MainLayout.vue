<template>
  <div>
    <Navbar />
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Navbar from './Navbar.vue'
</script>

<style scoped>
main {
  margin-top: 20px;
  padding: 10px;
}
</style>
