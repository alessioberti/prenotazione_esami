import { ref } from 'vue'
import api from './useApi'

const isLoggedIn = ref(false)
const userInfo = ref(null)

export function useAuth() {
  const login = async (email, password) => {
    try {
  
      await api.post('/login', { email, password })
      const resp = await api.get('/mylogin')
      userInfo.value = resp.data
      isLoggedIn.value = true
    
    } catch (err) {

      console.error('Errore durante il login:', err)
      isLoggedIn.value = false
      userInfo.value = null
      throw err
      
    }
  }

  const logout = async () => {
    try {
      await api.post('/logout')
    } catch (err) {
      console.error('Errore durante il logout:', err)
    }
    isLoggedIn.value = false
    userInfo.value = null
  }

  const checkAuth = async () => {
    try {
      const resp = await api.get('/mylogin')
      userInfo.value = resp.data
      isLoggedIn.value = true
    } catch (err) {
      console.error('Errore durante il checkAuth:', err)
      isLoggedIn.value = false
      userInfo.value = null
    }
  }

  return {
    isLoggedIn,
    userInfo,
    login,
    logout,
    checkAuth
  }
}
