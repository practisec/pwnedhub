var Signup = Vue.component('signup', {
    template: `
        <div class="signup">
            <about-static></about-static>
            <div>
                <signup-form></signup-form>
            </div>
        </div>
    `,
});

Vue.component('about-static', {
    template: `
        <div class="flex-column about">
            <h3>Welcome to Pwned<span class="red"><b>Hub</b></span>!</h3>
            <p>The ability to consolidate and organize testing tools and results during client engagements is key for consultants dealing with short timelines and high expectations. Unfortunately, today's options for cloud resourced security testing are poorly designed and fail to support even the most basic needs. PwnedHub attempts to solve this problem by providing a space to share knowledge, execute test cases, and store the results.</p>
            <p>Developed by child prodigies Cooper ("Cooperman"), Taylor ("Babygirl#1"), and Tanner ("Hack3rPrincess"), PwnedHub was designed based on experience gained through months of security testing. The PwnedHub team is ambitions, talented, and so confident in their product, if you don't like it, they'll issue a full refund. No questions asked.</p>
            <p>So what are you waiting for? Signup today!</p>
        </div>
    `,
});

Vue.component('signup-form', {
    template: `
        <div class="flex-column form rounded">
            <label for="username">Username: *</label>
            <input name="username" type="text" v-model="signupForm.username" />
            <label for="email">Email: *</label>
            <input name="email" type="text" v-model="signupForm.email" />
            <label for="name">Display Name: *</label>
            <input name="name" type="text" v-model="signupForm.name" />
            <label for="avatar">Avatar URL:</label>
            <input name="avatar" type="text" v-model="signupForm.avatar" />
            <label for="signature">Signature:</label>
            <textarea name="signature" v-model="signupForm.signature"></textarea>
            <label for="password">Password: *</label>
            <div class="flex-column" style="position: relative;">
                <input id="password" name="password" type="password" v-model="signupForm.password" />
                <input type="button" class="show" tabindex="-1" onclick="toggleShow();" value="show" />
            </div>
            <label for="question">Question: *</label>
            <select name="question" v-model="signupForm.question">
                <option value="" disabled selected>Select a question</option>
                <option v-for="question in questions" v-bind:key="question.id" v-bind:value="question.id">{{ question.text }}</option>
            </select>
            <label for="answer">Answer: *</label>
            <input name="answer" type="text" v-model="signupForm.answer" />
            <input type="button" v-on:click="doSignup" value="Signup" />
        </div>
    `,
    data: function() {
        return {
            questions: [],
            signupForm: {
                username: "",
                email: "",
                name: "",
                avatar: "",
                signature: "",
                password: "",
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
                // populate a default selection
                //this.signupForm.question = this.questions[0].id;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        doSignup: function() {
            fetch(store.getters.getApiUrl+"/users", {
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(this.signupForm),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("createToast", json.message);
                this.$router.push({ name: "login" });
            })
            .catch(error => store.dispatch("createToast", error));
        },
    },
    created: function() {
        this.getQuestions();
    },
});
