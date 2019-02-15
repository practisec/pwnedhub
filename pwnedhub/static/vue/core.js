const routes = [
    {
        path: '/messages',
        name: "Messages",
        component: Messages,
    },
    /*{
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
    {
        path: '/mail/compose',
        name: "Compose",
        component: Compose,
    },
    {
        path: '/mail/reply/:letterId',
        name: "Reply",
        component: Reply,
        props: true,
    },*/
]

const router = new VueRouter({
    routes: routes,
})

const app = new Vue({
    el: "#app",
    router,
    methods: {
        getUserInfo: function() {
            fetch(this.URL_API_USER_READ.format("me"))
            .then(response => response.json())
            .then(json => {
                window.sessionStorage.setItem("userInfo", JSON.stringify(json));
            });
        },
    },
    created: function() {
        this.getUserInfo();
    },
});
