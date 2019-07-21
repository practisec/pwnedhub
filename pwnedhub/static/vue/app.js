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
            authRequired: true,
        },
    },
    {
        path: "/mail",
        name: "mail",
        component: Mail,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/mail/view/:letterId",
        name: "letter",
        component: Letter,
        props: true,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/mail/compose",
        name: "compose",
        component: Compose,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/mail/reply/:letterId",
        name: "reply",
        component: Reply,
        props: true,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "/profile/view/:userId",
        name: "profile",
        component: Profile,
        props: true,
        meta: {
            authRequired: true,
        },
    },
    {
        path: "*",
        redirect: "/messages",
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
            })
        } else {
            next()
        }
    } else {
        next()
    }
});

// initialize the store prior to instantiating the app to ensure
// the router.beforeEach check gets the proper isLoggedIn value
store.dispatch("initUserInfo");

const app = new Vue({
    el: "#app",
    router,
});
