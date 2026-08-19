import { createRouter, createWebHashHistory } from "vue-router";
import { getAuthToken } from "@/shared/lib/authStorage";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/components/login/LoginPage.vue"),
      meta: { public: true },
    },
    {
      path: "/",
      component: () => import("@/components/layout/DashboardLayout.vue"),
      redirect: { name: "users" },
      children: [
        {
          path: "users",
          name: "users",
          component: () => import("@/components/users/UsersPage.vue"),
        },
        {
          path: "nodes",
          name: "nodes",
          component: () => import("@/components/nodes/NodesPage.vue"),
        },
        {
          path: "hosts",
          name: "hosts",
          component: () => import("@/components/hosts/HostsPage.vue"),
        },
        {
          path: "settings",
          name: "settings",
          component: () => import("@/components/settings/SettingsPage.vue"),
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
