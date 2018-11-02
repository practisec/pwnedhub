const routes = [
    {
        path: '/messages',
        name: "Messages",
        component: Messages,
    },
    {
        path: '/mail',
        name: "Mail",
        component: Mail,
    },
    {
        path: '/mail/view/:envelopeId',
        name: "Letter",
        component: Letter,
        props: true,
    },
]

const router = new VueRouter({
    routes: routes,
})

const app = new Vue({
    el: "#app",
    router,
});
