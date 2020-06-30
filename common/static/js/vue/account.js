var Account = Vue.component("account", {
    template: `
        <div v-if="user" class="flex-column account">
            <div class="avatar center-content"><router-link v-bind:to="{ name: 'profile', params: {userId: user.id} }" class="center"><img class="circular bordered-dark" v-bind:src="user.avatar" title="Avatar" /></router-link></div>
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
            <label for="new_password">New Password:</label>
            <div class="flex-column" style="position: relative;">
                <input id="password" name="new_password" v-model="userForm.new_password" type="password" />
                <input type="button" class="show" tabindex="-1" onclick="toggleShow();" value="show" />
            </div>
            <label for="question">Question: *</label>
            <select name="question" v-model="userForm.question">
                <option value="" disabled selected>Select a question</option>
                <option v-for="question in questions" v-bind:key="question.id" v-bind:value="question.id">{{ question.text }}</option>
            </select>
            <label for="answer">Answer: *</label>
            <input name="answer" v-model="userForm.answer" type="text" />
            <input type="button" v-on:click="doFormUser" value="Submit" />
        </div>
    `,
    data: function() {
        return {
            user: null,
            questions: [],
            userForm: {
                name: "",
                avatar: "",
                signature: "",
                new_password: "",
                question: "",
                answer: "",
            },
        }
    },
    methods: {
        getUser: function() {
            fetch(store.getters.getApiUrl+"/users/me", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.user = json;
                this.userForm.name = this.user.name
                this.userForm.avatar = this.user.avatar
                this.userForm.signature = this.user.signature
                this.userForm.question = this.user.question
                this.userForm.answer = this.user.answer
            })
            .catch(error => store.dispatch("createToast", error));
        },
        getQuestions: function() {
            fetch(store.getters.getApiUrl+"/questions")
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.questions = json.questions;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        doFormUser: function() {
            this.doUserUpdate(this.userForm);
        },
        doUserUpdate: function(payload) {
            fetch(store.getters.getApiUrl+"/users/"+this.user.id, {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "PATCH",
                body: JSON.stringify(payload),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.handleUpdate(json))
            .catch(error => this.updateFailed(error));
        },
        handleUpdate: function(json) {
            this.user = json;
            this.userForm.name = this.user.name;
            this.userForm.avatar = this.user.avatar;
            this.userForm.signature = this.user.signature;
            this.userForm.new_password = "";
            this.userForm.question = this.user.question;
            this.userForm.answer = this.user.answer;
            store.dispatch("createToast", 'Account updated.');
        },
        updateFailed: function(error) {
            store.dispatch("createToast", error);
        },
    },
    created: function() {
        this.getQuestions();
        // might need to wait here or ?s might not populate
        this.getUser();
    },
});
