const routes = [
    {
        path: "/login",
        name: "login",
        component: Login,
    },
    {
        path: "/messages",
        name: "messages",
        component: Messages,
        meta: {
            authRequired: true
        }
    },
    {
        path: "*",
        redirect: "/login"
    }
];

const router = new VueRouter({
    routes: routes,
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.authRequired)) {
        if (sessionStorage.getItem("userInfo") == null) {
            next({
                name: "login",
                params: { nextUrl: to.fullPath }
            })
        } else {
            next()
        }
    } else {
        next()
    }
});

const app = new Vue({
    el: "#app",
    router,
});
