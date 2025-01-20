import { createRouter, createWebHistory } from "vue-router";
import Login from "@/views/Login.vue";
import Slots from "@/views/Slots.vue";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/slots", name: "Slots", component: Slots },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
