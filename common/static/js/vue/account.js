var Account = Vue.component("account", {
    template: `
        <div v-if="user" class="account">
            <div>
                <div class="avatar center-content"><router-link v-bind:to="{ name: 'profile', params: {userId: user.id} }" class="center"><img class="circular bordered-dark" v-bind:src="user.avatar" title="Avatar" /></router-link></div>
                <update-password-form v-bind:user="user"></update-password-form>
            </div>
            <div>
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
            <input name="username" type="text" v-bind:value="user.username" disabled />
            <label for="email">Email:</label>
            <input name="email" type="text" v-bind:value="user.email" disabled />
            <label for="avatar">Avatar URL:</label>
            <input name="avatar" v-model="userForm.avatar" type="text"/>
            <label for="signature">Signature:</label>
            <textarea name="signature" v-model="userForm.signature"></textarea>
            <label for="name">Display Name: *</label>
            <input name="name" v-model="userForm.name" type="text" />
            <label for="question">Question: *</label>
            <select name="question" v-model="userForm.question">
                <option value="" disabled selected>Select a question</option>
                <option v-for="question in questions" v-bind:key="question.id" v-bind:value="question.id">{{ question.text }}</option>
            </select>
            <label for="answer">Answer: *</label>
            <input name="answer" v-model="userForm.answer" type="text" />
            <input type="button" v-on:click="updateUser" value="Update my account information." />
        </div>
    `,
    data: function() {
        return {
            questions: [],
            userForm: {
                name: "",
                avatar: "",
                signature: "",
                question: "",
                answer: "",
            },
        }
    },
    methods: {
        getQuestions: function() {
            fetch(store.getters.getApiUrl+"/questions")
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.questions = json.questions;
                this.userForm.question = this.user.question;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        setFormValues: function(user) {
            this.userForm.name = user.name
            this.userForm.avatar = user.avatar
            this.userForm.signature = user.signature
            this.userForm.question = user.question
            this.userForm.answer = user.answer
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
        this.getQuestions();
    },
});
