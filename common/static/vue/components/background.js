Vue.component("background", {
    template: `
        <div class="background" v-bind:class="isLoggedIn ? 'background-auth' : 'background-unauth'"></div>
    `,
    computed: {
        isLoggedIn: function() {
            return store.getters.isLoggedIn;
        }
    },
});
