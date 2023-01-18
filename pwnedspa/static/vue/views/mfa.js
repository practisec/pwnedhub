var Mfa = Vue.component('mfa', {
    template: `
        <div class="flex-column mfa">
            <div class="flex-column form rounded">
                <h3>Check your email.</h3>
                <p>A Multi-Factor Authentication code has been emailed to you.</p>
                <label for="code">MFA code:</label>
                <input name="code" type="text" v-model="codeForm.code" />
                <input type="button" v-on:click="submitCode" value="Yes, it's really me." />
            </div>
        </div>
    `,
    data: function() {
        return {
            codeForm: {
                code: "",
                code_token: "",
            },
        }
    },
    methods: {
        submitCode: function() {
            this.codeForm.code_token = store.getters.getMfaToken;
            fetch(store.getters.getApiUrl+"/access-token", {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(this.codeForm),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleMfaSuccess(json))
            .catch(error => this.handleMfaFailure(error));
        },
        handleMfaSuccess: function(json) {
            if (json.access_token && json.user) {
                // store auth data as necessary
                store.dispatch("setAuthInfo", json);
                // route appropriately
                if (this.$route.params.nextUrl != null) {
                    // originally requested location
                    this.$router.push(this.$route.params.nextUrl);
                } else {
                    // fallback landing page
                    if (json.user.role === "admin") {
                        this.$router.push({ name: "users" });
                    } else {
                        this.$router.push({ name: "notes" });
                    }
                }
            } else {
                this.handleMfaFailure(json.message);
            }
        },
        handleMfaFailure: function(error) {
            store.dispatch("unsetAuthInfo");
            store.dispatch("createToast", error);
        },
    },
    beforeDestroy () {
        store.dispatch("unsetMfaToken");
    },
});
