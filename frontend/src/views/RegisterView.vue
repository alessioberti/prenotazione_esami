<template>
    <div class="container">
        <form @submit.prevent="handleRegister">
            <div class="form-header">
                <h2 class="title-page">Registrazione</h2>
            </div>
            <div class="form-body">
                <div class="form-group-row">
                    <div class="form-group">
                        <label for="firstName" class="label">Nome</label>
                        <input
                            id="firstName"
                            type="text"
                            v-model="first_name"
                            required
                            placeholder="Inserisci nome"
                            class="button-generic"
                        />
                    </div>
                    <div class="form-group">
                        <label for="lastName" class="label">Cognome</label>
                        <input
                            id="lastName"
                            type="text"
                            v-model="last_name"
                            required
                            placeholder="Inserisci cognome"
                            class="button-generic"
                        />
                    </div>
                </div>
                <div class="form-group">
                    <label for="email" class="label">Email</label>
                    <input
                        id="email"
                        type="email"
                        v-model="email"
                        required
                        pattern="^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
                        placeholder="Inserisci email"
                        class="button-generic"
                    />
                </div>
                <div class="form-group">
                    <label for="password" class="label">Password</label>
                    <input
                        id="password"
                        type="password"
                        v-model="password"
                        required
                        minlength="8"
                        maxlength="32"
                        pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,32}$"
                        placeholder="da 8 a 32 caratteri (Az-09-!@#$%_&*)"
                        class="button-generic"
                    />
                </div>
                <div class="form-group">
                    <label for="confirmPassword" class="label">Conferma Password</label>
                    <input
                        id="confirmPassword"
                        type="password"
                        v-model="confirmPassword"
                        required
                        minlength="8"
                        maxlength="32"
                        placeholder="Conferma la tua password"
                        class="button-generic"
                    />
                    <p v-if="passwordMismatch" class="error">Le password non corrispondono.</p>
                </div>
                <div class="form-group">
                    <label for="telNumber" class="label">Telefono</label>
                    <input
                        id="telNumber"
                        type="text"
                        v-model="telNumber"
                        required
                        pattern="^\+?\d{10,13}$"
                        placeholder="Inserisci telefono (es. +391234567890)"
                        class="button-generic"
                    />
                </div>
                <button :disabled="loading || passwordMismatch" type="submit" class="button">Registrati</button>
            </div>
        </form>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="message" class="success">{{ message }}</p>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../composables/useApi';

const router = useRouter();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const telNumber = ref('');
const first_name = ref('');
const last_name = ref('');

const error = ref(null);
const message = ref(null);
const loading = ref(false);

const passwordMismatch = computed(() => password.value !== confirmPassword.value);

const handleRegister = async () => {
    if (passwordMismatch.value) return;

    try {
        error.value = null;
        message.value = null;
        loading.value = true;

        const response = await api.post('/register', {
            email: email.value,
            password: password.value,
            tel_number: telNumber.value,
            first_name: first_name.value,
            last_name: last_name.value,
        });

        message.value = response.data.message || 'Registrazione completata!';

        router.push('/login');
    } catch (err) {
        error.value = err?.response?.data?.error || 'Errore di registrazione';
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
</style>
