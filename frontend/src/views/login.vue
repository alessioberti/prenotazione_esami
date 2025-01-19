<template>
    <div>
        <h1>Login</h1>
        <form @submit.prevent="login">
            <input type="text" v-model="username" placeholder="Username" />
            <input type="password" v-model="password" placeholder="Password" />
            <button type="submit">Login</button>
        </form>
        <p v-if="error">{{ error }}</p>
    </div>
</template>

<script>
import axios from "@/api/axios";

export default {
    data() {
        return {
            username: "",
            password: "",
            error: null,
        };
    },
    methods: {
        async login() {
            try {
                const response = await axios.post("/login", {
                    username: this.username,
                    password: this.password,
                });
                localStorage.setItem("token", response.data.access_token);
                this.$router.push("/slots");
            } catch (err) {
                this.error = "Login failed. Check your credentials.";
            }
        },
    },
};
</script>