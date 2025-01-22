import { ref } from 'vue'
import api from './useApi' // se esiste


const isLoggedIn = ref(false)
const userInfo = ref(null)

export function useAuth() {
  const login = async () => {
    isLoggedIn.value = true
   
    await getUserInfo()
  }

  const logout = async () => {
    try {
      await api.post('/logout')
    } catch (err) {
      console.error('Errore logout', err)
    }
    isLoggedIn.value = false
    userInfo.value = null
  }

  const getUserInfo = async () => {
    try {
      const resp = await api.get('/mylogin')
      userInfo.value = resp.data
      isLoggedIn.value = true
    } catch (err) {
      console.error('Errore getUserInfo:', err)
      isLoggedIn.value = false
      userInfo.value = null
      throw err
    }
  }

  return { isLoggedIn, userInfo, login, logout, getUserInfo }
}
