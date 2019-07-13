var Login = Vue.component('login', {
    template: `
        <div class="flex-grow">
            <p v-if="error" class="red">{{ error }}</p>
        </div>
    `,
    data: function() {
        return {
            error: false,
        }
    },
    methods: {
        getUserInfo: function() {
            session = ('; ' + document.cookie).split("; " + "session" + "=").pop().split(';').shift()
            fetch(this.URL_API_BASE+"/access-token", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify({session: session}),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.logIn(json))
            .catch(error => this.loginFailed(error))
        },
        logIn: function(json) {
            if (!json.id) {
                this.loginFailed("Malformed user response received.");
                return;
            }
            //[vuln] not really a vuln, but can change "user" to "admin" to see other functionality in the interface
            sessionStorage.setItem("userInfo", JSON.stringify(json));
            this.error = "Login successful!";
            if (this.$route.params.nextUrl != null){
                // originally requested location
                this.$router.push(this.$route.params.nextUrl);
            } else {
                // fallback landing page
                this.$router.push('messages');
            }
        },
        loginFailed: function(error) {
            this.error = error;
            sessionStorage.clear();
        },
    },
    created: function() {
        this.getUserInfo();
    },
});
