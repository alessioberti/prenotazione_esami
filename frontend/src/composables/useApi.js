import axios from 'axios'

const api = axios.create({
  baseURL: 'https://localhost:10000',
  withCredentials: true
})

api.interceptors.request.use((config) => {
  
  const csrfToken = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrf_access_token='))
    ?.split('=')[1]

  if (csrfToken) {
    config.headers['X-CSRF-TOKEN'] = csrfToken
  }

  return config
}, (error) => Promise.reject(error))

export default api