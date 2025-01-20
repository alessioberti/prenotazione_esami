import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:10000", // URL del backend Flask
  timeout: 10000,
  headers: {
    "Content-Type": "application/json", // Indica che stai inviando JSON
  },
  withCredentials: false, // Cambia a true solo se il backend richiede cookie
});

export default instance;
