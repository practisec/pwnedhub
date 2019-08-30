var Login = Vue.component('login', {
    template: `
        <div class="flex-width-8 flex-offset-2 flex-basis-8">
            <div class="flex-column">
                <label for="username">Username:</label>
                <input name="username" type="text" v-model="loginForm.username" />
                <label for="password">Password:</label>
                <div class="flex-column" style="position: relative;">
                    <input id="password" name="password" type="password" v-model="loginForm.password" />
                    <input type="button" class="show" tabindex="-1" onclick="toggleShow();" value="show" />
                </div>
                <input type="button" v-on:click="doFormLogin" value="Login" />
                <hr>
                <div class="center-content">
                    <google-oidc v-on:done="doOIDCLogin" />
                </div>
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
        doFormLogin: function() {
            this.doLogin(this.loginForm);
        },
        doOIDCLogin: function(user) {
            var payload = {
                id_token: user.getAuthResponse().id_token
            };
            this.doLogin(payload);
        },
        doLogin: function(payload) {
            fetch(store.getters.getApiUrl+"/access-token", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(payload),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleLogin(json))
            .catch(error => this.loginFailed(error));
        },
        handleLogin: function(json) {
            if (!json.id) {
                this.loginFailed(json.message);
                return;
            }
            store.dispatch("setUserInfo", json);
            if (this.$route.params.nextUrl != null) {
                // originally requested location
                this.$router.push(this.$route.params.nextUrl);
            } else {
                // fallback landing page
                this.$router.push('messages');
            }
        },
        loginFailed: function(error) {
            store.dispatch("unsetUserInfo");
            showFlash(error);
        },
    },
});

Vue.component('google-oidc', {
    template: `
        <img id="signinBtn" class="oidc-button" src="/images/google_signin.png" />
    `,
    mounted: function() {
        gapi.load('auth2', function() {
            const auth2 = window.gapi.auth2.init({
                cookiepolicy: 'single_host_origin',
            });
            auth2.attachClickHandler(
                "signinBtn",
                {},
                function(googleUser) {
                    this.$emit('done', googleUser);
                }.bind(this),
                function(error) {
                    if (error.error === "network_error") {
                        showFlash("OpenID Connect provider unreachable.");
                    } else if (error.error !== "popup_closed_by_user") {
                        showFlash("OpenID Connect error ({0}).".format(error.error));
                    }
                },
            );
        }.bind(this));
    },
});
