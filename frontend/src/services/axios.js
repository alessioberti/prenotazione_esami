// src/services/axios.js
import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:10000",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const csrfToken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrf_access_token="))
    ?.split("=")[1];

  if (csrfToken) {
    config.headers["X-CSRF-TOKEN"] = csrfToken;
  }
  config.withCredentials = true;
  return config;
});

export default instance;
