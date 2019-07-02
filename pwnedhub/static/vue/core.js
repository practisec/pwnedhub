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
            session = ('; ' + document.cookie).split("; " + "session" + "=").pop().split(';').shift()
            fetch(this.URL_API_BASE+"/access-token", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify({session: session}),
                headers:{"Content-Type": "application/json"}
            })
            .then(response => response.json())
            .then(json => {
                //[vuln] not really a vuln, but can change "user" to "admin" to see other functionality in the interface
                window.sessionStorage.setItem("userInfo", JSON.stringify(json));
            });
        },
    },
    created: function() {
        this.getUserInfo();
    },
});
