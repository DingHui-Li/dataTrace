import { createWebHistory, createRouter, RouteRecordRaw } from "vue-router";

const pages = import.meta.glob("../views/**/**.vue");
const routes: Array<RouteRecordRaw> = [];
Object.keys(pages).map(function (key: string) {
  const component = pages[key];
  const path = key
    .toLowerCase()
    .replace(/\.vue$/, "")
    .replace(/.+\/views/g, "");
  if (!path.includes("/components")) {
    routes.push({
      path,
      name: path,
      component,
    });
  }
});
console.log(routes);
export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/home",
    },
    ...routes,
  ],
});
