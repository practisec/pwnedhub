Vue.component("navigation", {
    template: `
        <div class="header">
            <div class="container-fluid nav">
                <ul class="menu" v-bind:class="{ active: isOpen }">
                    <li class="brand"><img src="/images/logo.png" /></li>
                    <li class="toggle"><a href="#" v-on:click="toggleMenu"><i class="fas fa-bars"></i></a></li>
                    <li class="item avatar" v-if="isLoggedIn">
                        <router-link v-bind:to="{ name: 'account' }">
                            <img class="circular bordered-dark" v-bind:src="userAvatar" title="Avatar" />
                        </router-link>
                    </li>
                    <li class="item" v-for="route in permissions[userRole]" v-bind:key="route.id" v-bind:route="route">
                        <router-link v-bind:to="{ name: route.name, params: route.params || {} }">{{ route.text }}</router-link>
                    </li>
                    <li class="item" v-if="isLoggedIn"><span v-on:click="doLogout">Logout</span></li>
                </ul>
            </div>
        </div>
    `,
    data: function() {
        return {
            isOpen: false,
            permissions: {
                guest: [
                    {
                        id: 0,
                        text: "Login",
                        name: "login",
                    },
                    {
                        id: 1,
                        text: "Signup",
                        name: "signup",
                    },
                ],
                admin: [
                    {
                        id: 0,
                        text: "PwnMail",
                        name: "mail",
                    },
                    {
                        id: 1,
                        text: "Messages",
                        name: "messages",
                    },
                    {
                        id: 2,
                        text: "Tools",
                        name: "tools",
                    },
                    {
                        id: 3,
                        text: "Users",
                        name: null,
                    },
                ],
                user: [
                    {
                        id: 0,
                        text: "Notes",
                        name: "notes",
                    },
                    {
                        id: 1,
                        text: "Artifacts",
                        name: null,
                    },
                    {
                        id: 2,
                        text: "Scans",
                        name: "scans",
                    },
                    {
                        id: 3,
                        text: "PwnMail",
                        name: "mail",
                    },
                    {
                        id: 4,
                        text: "Messages",
                        name: "messages",
                    },
                ],
            }
        }
    },
    watch: {
        '$route': function() {
            this.isOpen = false;
        },
    },
    computed: {
        isLoggedIn: function() {
            return store.getters.isLoggedIn;
        },
        userRole: function() {
            return store.getters.getUserRole;
        },
        userAvatar: function() {
            return store.getters.getUserInfo.avatar;
        },
    },
    methods: {
        doLogout: function() {
            fetch(store.getters.getApiUrl+"/access-token", {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => {
                store.dispatch("unsetAuthInfo");
                this.$router.push({ name: "login" });
            })
            .catch(error => store.dispatch("createToast", error));
        },
        toggleMenu: function() {
            this.isOpen = !this.isOpen;
        },
    },
});
