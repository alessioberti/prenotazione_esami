<template>
    <div class="justify-center w-full flex">
      <h2 class="title-page">Sistema di prenotazione</h2>
    </div>
    <div class="divide-y divide-gray-200 overflow-hidden rounded-lg bg-gray-200 shadow sm:grid sm:grid-cols-2 sm:gap-px sm:divide-y-0">
  <div @click="goToBook" class="cursor-pointer hover:bg-gray-100 group relative rounded-tl-lg rounded-tr-lg bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 sm:rounded-tr-none">
    <div>
      <span class="inline-flex rounded-lg bg-teal-50 p-3 text-teal-700 ring-4 ring-white">
        <svg class="size-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true" data-slot="icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      </span>
    </div>
    <div class="mt-8">
      <h3 class="text-base font-semibold text-gray-900">
        
          <span class="absolute inset-0" aria-hidden="true"></span>
          Prenota un Esame
       
      </h3>
      <p class="mt-2 text-sm text-gray-500">Effettua una nuova prenotazione</p>
    </div>
    <span class="pointer-events-none absolute right-6 top-6 text-gray-300 group-hover:text-gray-400" aria-hidden="true">
      <svg class="size-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
      </svg>
    </span>
  </div>
  <div @click="goToManage" class="cursor-pointer hover:bg-gray-100 group relative bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 sm:rounded-tr-lg">
    <div>
      <span class="inline-flex rounded-lg bg-purple-50 p-3 text-purple-700 ring-4 ring-white">
        <svg class="size-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true" data-slot="icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
        </svg>
      </span>
    </div>
    <div class="mt-8">
      <h3 class="text-base font-semibold text-gray-900">
          <span class="absolute inset-0" aria-hidden="true"></span>
          Gestisci Prenotazioni
      </h3>
      <p class="mt-2 text-sm text-gray-500">Consulta la lista delle tue prenotazioni. In questa sezione potrai anche richiedere l'<strong>annullamento</strong> di una prenotazione o procedere con il <strong>pagamento on-line</strong></p>
    </div>
    <span class="pointer-events-none absolute right-6 top-6 text-gray-300 group-hover:text-gray-400" aria-hidden="true">
      <svg class="size-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
      </svg>
    </span>
  </div>

</div>

  </template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  
  const router = useRouter()
  const { logout } = useAuth()
  
  const goToBook = () => {
    router.push({ name: 'book' })
  }
  
  const goToManage = () => {
    router.push({ name: 'manage' })
  }
  
  </script>
  
  <style scoped>
  .home-container {
    text-align: center;
    margin-top: 50px;
  }
  </style>
  