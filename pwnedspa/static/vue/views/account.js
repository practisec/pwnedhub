var Account = Vue.component("account", {
    template: `
        <div v-if="user" class="account">
            <div class="flex-column flex-justify-end">
                <div class="flex-grow flex-row flex-align-center">
                    <div class="avatar">
                        <router-link v-bind:to="{ name: 'profile', params: {userId: user.id} }" class="flex-grow">
                            <img class="circular bordered-dark" v-bind:src="user.avatar" title="Avatar" />
                        </router-link>
                    </div>
                </div>
                <update-password-form v-bind:user="user"></update-password-form>
            </div>
            <div class="flex-column flex-justify-end">
                <update-account-form v-bind:user="user"></update-account-form>
            </div>
        </div>
    `,
    computed: {
        user: function() {
            return store.getters.getUserInfo;
        }
    },
});

Vue.component("update-password-form", {
    props: {
        user: Object,
    },
    template: `
        <div class="flex-column form">
            <label for="new_password">New Password:</label>
            <password-field name="new_password" v-model="passwordForm.new_password"></password-field>
            <label for="current_password">Current Password:</label>
            <password-field name="current_password" v-model="passwordForm.current_password"></password-field>
            <input type="button" v-on:click="updatePassword" value="Update my password." />
        </div>
    `,
    data: function() {
        return {
            passwordForm: {
                new_password: "",
                current_password: "",
            },
        }
    },
    methods: {
        updatePassword: function() {
            fetch(store.getters.getApiUrl+"/users/"+this.user.id+"/password", {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "PUT",
                body: JSON.stringify(this.passwordForm),
            })
            .then(handleErrors)
            .then(response => {
                this.passwordForm.new_password = "";
                this.passwordForm.current_password = "";
                store.dispatch("createToast", "Password updated.");
            })
            .catch(error => store.dispatch("createToast", error));
        },
    },
});

Vue.component("update-account-form", {
    props: {
        user: Object,
    },
    template: `
        <div class="flex-column form">
            <label for="username">Username:</label>
            <input name="username" type="text" v-model="userForm.username" />
            <label for="email">Email:</label>
            <input name="email" type="text" v-model="userForm.email" />
            <label for="avatar">Avatar URL:</label>
            <input name="avatar" v-model="userForm.avatar" type="text"/>
            <label for="signature">Signature:</label>
            <textarea name="signature" v-model="userForm.signature"></textarea>
            <label for="name">Display Name:</label>
            <input name="name" v-model="userForm.name" type="text" />
            <input type="button" v-on:click="updateUser" value="Update my account information." />
        </div>
    `,
    data: function() {
        return {
            userForm: {
                username: "",
                email: "",
                name: "",
                avatar: "",
                signature: "",
            },
        }
    },
    methods: {
        setFormValues: function(user) {
            this.userForm.username = user.username
            this.userForm.email = user.email
            this.userForm.name = user.name
            this.userForm.avatar = user.avatar
            this.userForm.signature = user.signature
        },
        updateUser: function() {
            fetch(store.getters.getApiUrl+"/users/"+this.user.id, {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "PATCH",
                body: JSON.stringify(this.userForm),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("createToast", 'Account updated.');
                store.dispatch("setAuthInfo", { user: json });
            })
            .catch(error => store.dispatch("createToast", error));
        },
    },
    created: function() {
        this.setFormValues(this.user);
    },
});
