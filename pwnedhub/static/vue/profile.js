var Profile = Vue.component("profile", {
    props: {
        userId: [Number, String],
    },
    template: `
        <div v-if="user" class="flex-width-6 flex-offset-3 flex-basis-6 profile-view center-content">
            <div class="avatar"><img class="circular bordered-dark" v-bind:src="user.avatar" title="Avatar" /></div>
            <div><h3>{{ user.name }}</h3></div>
            <div><h6>Member since: {{ user.created }}</h6></div>
            <div><blockquote>{{ user.signature }}</blockquote></div>
            <div><h6>Reputation:</h6></div>
            <div><h1>{{ user.reputation }}</h1></div>
        </div>
    `,
    data: function() {
        return {
            user: null,
        }
    },
    methods: {
        getUser: function() {
            fetch(this.URL_API_BASE+"/users/"+this.userId, {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.user = json;
            });
        },
    },
    created: function() {
        this.getUser();
    },
});
