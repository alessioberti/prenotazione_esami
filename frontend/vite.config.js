import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    https: {
      key: '/Users/ale/prenotazioni_esami/prenotazione_esami/certs/key.pem',
      cert: '/Users/ale/prenotazioni_esami/prenotazione_esami/certs/cert.pem',
    }
  }
})