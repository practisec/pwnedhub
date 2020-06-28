var Login = Vue.component('login', {
    template: `
        <div class="login">
            <index-static></index-static>
            <login-form></login-form>
            <div class="flex-row flex-wrap flex-justify-space-evenly center-content panels">
                <div>
                    <h5>Scan.</h5>
                    <i class="fas fa-search large" title="Find"></i>
                </div>
                <div>
                    <h5>Find.</h5>
                    <i class="fas fa-bug large" title="Bug"></i>
                </div>
                <div>
                    <h5>Win.</h5>
                    <i class="fas fa-dollar-sign large" title="Bounty"></i>
                </div>
            </div>
        </div>
    `,
});

Vue.component('index-static', {
    template: `
        <div class="flex-column">
            <div>
                <img style="max-width: 100%;" src="/images/logo.png" />
            </div>
            <div class="center-content">
                <h3>A <span class="red">collaborative</span> space to conduct <span class="red">hosted</span> security assessments.</h3>
            </div>
        </div>
    `,
});

Vue.component('login-form', {
    template: `
        <div>
            <div class="flex-column form rounded">
                <label for="username">Username:</label>
                <input name="username" type="text" v-model="loginForm.username" />
                <label for="password">Password:</label>
                <div class="flex-column" style="position: relative;">
                    <input id="password" name="password" type="password" v-model="loginForm.password" />
                    <input type="button" class="show" tabindex="-1" onclick="toggleShow();" value="show" />
                </div>
                <input type="button" v-on:click="doFormLogin" value="Login" />
                <div class="gutter-bottom center-content bolded">OR</div>
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
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(payload),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleLogin(json))
            .catch(error => this.loginFailed(error));
        },
        handleLogin: function(json) {
            if (!json.user) {
                this.loginFailed(json.message);
                return;
            }
            // store auth data as necessary
            store.dispatch("setAuthInfo", json);
            // route appropriately
            if (this.$route.params.nextUrl != null) {
                // originally requested location
                this.$router.push(this.$route.params.nextUrl);
            } else {
                // fallback landing page
                this.$router.push("messages");
            }
        },
        loginFailed: function(error) {
            store.dispatch("unsetAuthInfo");
            store.dispatch("createToast", error);
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
                        store.dispatch("createToast", "OpenID Connect provider unreachable.");
                    } else if (error.error !== "popup_closed_by_user") {
                        store.dispatch("createToast", "OpenID Connect error ({0}).".format(error.error));
                    }
                },
            );
        }.bind(this));
    },
});
