/****************************************
 ***************** Router ***************
 ****************************************/
import Vue from "vue";
import VueRouter from "vue-router";

import Dashboard from "./components/pages/Dashboard";

Vue.use(VueRouter);

export const routeNames = {
  ROOT: "root",
  DASHBOARD: "dashboard"
};

Vue.prototype.$rns = routeNames;

const router = new VueRouter({
  scrollBehavior: function(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { x: 0, y: 0 };
    }
  },
  routes: [
    {
      path: "/",
      name: routeNames.ROOT,
      redirect: { name: routeNames.DASHBOARD }
    },
    {
      path: "/dashboard",
      name: routeNames.DASHBOARD,
      meta: {
        pageInfo: {
          title: "Dashboard",
          titleDesc: "reports & statistics"
        }
      },
      component: Dashboard
    },
    {
      path: "*",
      redirect: { name: routeNames.DASHBOARD }
    }
  ]
});

router.afterEach(function(toRoute) {
  var title = "Chills-Students :: ",
    pageInfo = toRoute.meta.pageInfo || {};
  if (pageInfo.title) {
    title = title + pageInfo.title + " :: ";
  }
  if (pageInfo.titleDesc) {
    title = title + pageInfo.titleDesc;
  }
  window.document.title = title;
});

export default router;
