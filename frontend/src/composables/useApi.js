import axios from 'axios'
import { useAuth } from './useAuth'


const api = axios.create({
  baseURL: 'http://localhost:10000', 

})


api.interceptors.request.use(
  (config) => {
    const { token } = useAuth()
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default api
