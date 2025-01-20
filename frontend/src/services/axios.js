import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:10000", // URL del backend
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor per aggiungere il token JWT a tutte le richieste
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default instance;
