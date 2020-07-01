var ResetInit = Vue.component('reset-init', {
    template: `
        <div class="flex-column reset">
            <h3>Forgot your password?</h3>
            <p>Don't worry. It happens to the best of us.</p>
            <label for="credential">Email address or username:</label>
            <input name="credential" type="text" v-model="credentialForm.credential" />
            <input type="button" v-on:click="doInitializeReset" value="Please email me a recovery link." />
        </div>
    `,
    data: function() {
        return {
            credentialForm: {
                credential: "",
            },
        }
    },
    methods: {
        doInitializeReset: function() {
            fetch(store.getters.getApiUrl+"/password-reset", {
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(this.credentialForm),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleSuccess(json))
            .catch(error => this.handleFailure(error));
        },
        handleSuccess: function(json) {
            this.credentialForm.credential = "";
            store.dispatch("createToast", json.message);
            setTimeout(function() {
                alert("You've got mail!");
            }, 2000);
        },
        handleFailure: function(error) {
            store.dispatch("createToast", error);
        },
    },
});

var ResetPassword = Vue.component('reset-password', {
    props: {
        userId: [Number, String],
        token: String,
    },
    template: `
        <div class="flex-column reset">
            <h3>Reset your password!</h3>
            <p>And if you need us again, we'll be here, ready to help.</p>
            <label for="password">New password:</label>
            <div class="flex-column" style="position: relative;">
                <input id="password" name="password" type="password" v-model="passwordForm.new_password" />
                <input type="button" class="show" tabindex="-1" onclick="toggleShow();" value="show" />
            </div>
            <input type="button" v-on:click="doResetPassword" value="Please reset my password." />
        </div>
    `,
    data: function() {
        return {
            passwordForm: {
                new_password: "",
                token: this.token,
            }
        }
    },
    methods: {
        doResetPassword: function(payload) {
            fetch(store.getters.getApiUrl+"/users/"+this.userId+"/password", {
                headers: {"Content-Type": "application/json"},
                method: "PUT",
                body: JSON.stringify(this.passwordForm),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleSuccess(json))
            .catch(error => this.handleFailure(error));
        },
        handleSuccess: function(json) {
            store.dispatch("createToast", json.message);
            this.$router.push({ name: "login" });
        },
        handleFailure: function(error) {
            store.dispatch("createToast", error);
        },
    },
});
