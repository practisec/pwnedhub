var ResetInit = Vue.component('reset-init', {
    template: `
        <div class="flex-column reset">
            <div class="flex-column form rounded">
                <h3>Forgot your password?</h3>
                <p>Don't worry. It happens to the best of us.</p>
                <label for="credential">Email address or username:</label>
                <input name="credential" type="text" v-model="credentialForm.credential" />
                <input type="button" v-on:click="initializeReset" value="Please email me a recovery link." />
            </div>
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
        initializeReset: function() {
            fetch(store.getters.getApiUrl+"/password-reset", {
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(this.credentialForm),
            })
            .then(handleErrors)
            .then(response => {
                this.credentialForm.credential = "";
                store.dispatch("createToast", "Password reset email sent.");
            })
            .catch(error => store.dispatch("createToast", error));
        },
    },
});

var ResetPassword = Vue.component('reset-password-form', {
    props: {
        userId: [Number, String],
        token: String,
    },
    template: `
        <div class="flex-column reset">
            <div class="flex-column form rounded">
                <h3>Reset your password!</h3>
                <p>And if you need us again, we'll be here, ready to help.</p>
                <label for="new_password">New password:</label>
                <password-field name="new_password" v-model="passwordForm.new_password"></password-field>
                <input type="button" v-on:click="resetPassword" value="Please reset my password." />
            </div>
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
        resetPassword: function() {
            fetch(store.getters.getApiUrl+"/users/"+this.userId+"/password", {
                headers: {"Content-Type": "application/json"},
                method: "PUT",
                body: JSON.stringify(this.passwordForm),
            })
            .then(handleErrors)
            .then(response => {
                store.dispatch("createToast", "Password successfully reset.");
                this.$router.push({ name: "login" });
            })
            .catch(error => store.dispatch("createToast", error));
        },
    },
});
