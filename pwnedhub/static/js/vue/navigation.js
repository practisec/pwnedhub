var Navigation = Vue.component("navigation", {
    template: `
        <nav class="flex-grow container-fluid flex-row">
            <div class="brand">
                Pwned<span class="red"><b>Hub</b></span><span class="subscript">/m</span>
            </div>
            <div class="flex-grow flex-row flex-justify-right nav">
                <ul v-if="isLoggedIn" class="top-menu">
                    <li><img class="circular bordered-dark avatar" v-bind:src="getUserAvatar()" title="Avatar" />
                        <ul class="sub-menu">
                            <li v-for="route in links" v-bind:key="route.id" v-bind:route="route">
                                <router-link v-bind:to="{ name: route.name, params: route.params || {} }">{{ route.text }}</router-link>
                            </li>
                            <li>
                                <span v-on:click="doLogout">Logout</span>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </nav>
        `,
    data: function() {
        return {
            links: [
                {
                    id: 0,
                    text: "Messages",
                    name: "messages",
                },
                {
                    id: 1,
                    text: "Mail",
                    name: "mail",
                },
            ]
        }
    },
    computed: {
        isLoggedIn: function() {
            return store.getters.isLoggedIn;
        },
    },
    methods: {
        getUserAvatar: function() {
            return store.getters.getUserInfo.avatar;
        },
        doLogout: function() {
            fetch(store.getters.getApiUrl+"/access-token", {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => this.handleLogout())
            .catch(error => showFlash(error));
        },
        handleLogout: function() {
            store.dispatch("unsetUserInfo");
            this.$router.push('login');
        }
    }
});
