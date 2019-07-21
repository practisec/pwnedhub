var Login = Vue.component('login', {
    template: `
        <div class="flex-width-4 flex-offset-4 flex-basis-4">
            <div class="flex-column">
                <label for="username">Username:</label>
                <input name="username" type="text" v-model="loginForm.username" />
                <label for="password">Password:</label>
                <div class="flex-column" style="position: relative;">
                    <input id="password" name="password" type="password" v-model="loginForm.password" />
                    <input type="button" class="show" onclick="toggleShow();" value="show" />
                </div>
                <input type="button" v-on:click="doLogin" value="Login" />
            </div>
        </div>
    `,
    data: function() {
        return {
            loginForm: {
                username: "",
                password: "",
            },
        }
    },
    methods: {
        doLogin: function() {
            fetch(store.getters.getApiUrl+"/access-token", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(this.loginForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleLogin(json))
            .catch(error => this.loginFailed(error))
        },
        handleLogin: function(json) {
            if (!json.id) {
                this.loginFailed(json.message);
                return;
            }
            //[vuln] not really a vuln, but can change "user" to "admin" to see other functionality in the interface
            sessionStorage.setItem("userInfo", JSON.stringify(json));
            if (this.$route.params.nextUrl != null){
                // originally requested location
                this.$router.push(this.$route.params.nextUrl);
            } else {
                // fallback landing page
                this.$router.push('messages');
            }
        },
        loginFailed: function(error) {
            sessionStorage.clear();
            showFlash(error);
        },
    },
});
