import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://localhost:10000', // URL del backend Flask
    timeout: 10000, // Timeout di 10 secondi
});

export default instance;