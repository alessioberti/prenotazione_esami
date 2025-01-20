import { createRouter, createWebHistory } from "vue-router";
import Login from "../components/Login.vue";
import NewBooking from "../components/NewBooking.vue";
import ManageBookings from "../components/ManageBookings.vue";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/new-booking", name: "NewBooking", component: NewBooking },
  { path: "/manage-bookings", name: "ManageBookings", component: ManageBookings },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/*
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem("token");
    if (to.name !== "Login" && !token) {
      next({ name: "Login" }); 
      next(); 
    }
  });
*/
  export default router;