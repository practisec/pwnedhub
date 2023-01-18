const routes = [
    {
        path: "/signup",
        name: "signup",
        component: Signup,
    },
    {
        path: "/login",
        name: "login",
        component: Login,
    },
    {
        path: "/mfa",
        name: "mfa",
        component: Mfa,
    },
    {
        path: "/reset",
        name: "reset-init",
        component: ResetInit,
    },
    {
        path: "/reset/:userId/:token",
        name: "reset-password",
        component: ResetPassword,
        props: true,
    },
    {
        path: "/account",
        name: "account",
        component: Account,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/profile/:userId",
        name: "profile",
        component: Profile,
        props: true,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/notes",
        name: "notes",
        component: Notes,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/scans",
        name: "scans",
        component: Scans,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/messaging",
        name: "messaging",
        component: Messaging,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/admin/tools",
        name: "tools",
        component: Tools,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/admin/users",
        name: "users",
        component: Users,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "*",
        redirect: "/login",
    }
];

const router = new VueRouter({
    routes: routes,
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.authRequired)) {
        if (!store.getters.isLoggedIn) {
            next({
                name: "login",
                params: { nextUrl: to.fullPath }
            });
        } else {
            next();
        }
    } else {
        // the login/mfa views use similar logic to handle routing of the nextUrl parameter
        // all must be updated if there is a change
        if (store.getters.isLoggedIn) {
            if (store.getters.isAdmin) {
                next({ name: "users" });
            }
            next({ name: "notes" });
        } else {
            next();
        }
    }
});
