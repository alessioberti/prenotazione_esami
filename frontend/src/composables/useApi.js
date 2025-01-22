import axios from 'axios'

const api = axios.create({
  baseURL: 'https://localhost:10000',
  withCredentials: true
})
export default api