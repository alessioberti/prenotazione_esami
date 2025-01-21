import { ref } from 'vue'

const token = ref(localStorage.getItem('token') || null)

// isLoggedIn è true se esiste un token in memoria
const isLoggedIn = ref(!!token.value)

export function useAuth() {
  // Funzione per salvare token su login
  const login = (jwtToken) => {
    token.value = jwtToken
    localStorage.setItem('token', jwtToken)
    isLoggedIn.value = true
  }

  // Funzione per rimuovere token su logout
  const logout = () => {
    token.value = null
    localStorage.removeItem('token')
    isLoggedIn.value = false
  }

  return {
    token,
    isLoggedIn,
    login,
    logout
  }
}
