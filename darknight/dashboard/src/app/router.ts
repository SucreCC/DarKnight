import { createRouter, createWebHashHistory } from "vue-router";
import { getAuthToken } from "@/shared/lib/authStorage";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/pages/LoginPage.vue"),
      meta: { public: true },
    },
    {
      path: "/",
      component: () => import("@/layouts/DashboardLayout.vue"),
      redirect: { name: "users" },
      children: [
        {
          path: "users",
          name: "users",
          component: () => import("@/pages/UsersPage.vue"),
        },
        {
          path: "nodes",
          name: "nodes",
          component: () => import("@/pages/NodesPage.vue"),
        },
        {
          path: "hosts",
          name: "hosts",
          component: () => import("@/pages/HostsPage.vue"),
        },
        {
          path: "settings",
          name: "settings",
          component: () => import("@/pages/SettingsPage.vue"),
        },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: { name: "users" } },
  ],
});

router.beforeEach((to) => {
  const isPublic = to.meta.public === true;
  const hasToken = !!getAuthToken();
  if (!isPublic && !hasToken) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && hasToken) {
    return { name: "users" };
  }
  return true;
});

export default router;
