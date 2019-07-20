var Mail = Vue.component("mail", {
    template: `
        <div class="flex-grow inbox flex-row flex-justify-center">
            <table class="clickable">
                <caption class="left-content">
                    <input type="button" value="Compose" v-on:click="draftLetter" />
                </caption>
                <thead>
                    <tr>
                        <th>from</th>
                        <th>subject</th>
                        <th>date</th>
                    </tr>
                </thead>
                <tbody>
                    <envelope v-if="mail.length > 0" v-for="letter in mail" v-bind:key="letter.id" v-bind:letter="letter"></envelope>
                    <tr v-else>
                        <td colspan="4" class="center-content"><i class="fas fa-exclamation-circle medium" title="Empty"></i></td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    computed: {
        mail: function() {
            return store.getters.getMail;
        },
    },
    methods: {
        draftLetter: function() {
            this.$router.push({ name: 'compose' });
        },
    },
    beforeRouteEnter: function(to, from, next) {
        if (store.getters.getMail.length > 0) {
            next();
        } else {
            fetch(store.getters.getApiUrl+"/mail", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("updateMail", json.mail);
                next();
            });
        }
    },
});

Vue.component("envelope", {
    props: {
        letter: Object,
    },
    template: `
        <tr v-bind:style="!letter.read ? { fontWeight: 'bold' } : ''" v-on:click="openLetter">
            <td class="left-content">{{ letter.sender.name }}</td>
            <td class="left-content">{{ letter.subject }}</td>
            <td>{{ letter.created }}</td>
        </tr>
    `,
    methods: {
        openLetter: function() {
            this.$router.push({ name: 'letter', params: { letterId: this.letter.id } });
        },
    },
});

var Letter = Vue.component("letter", {
    props: {
        letterId: [Number, String],
    },
    template: `
        <div v-if="letter" class="flex-width-10 flex-offset-1 flex-basis-10 mail">
            <div>
                <h5>{{ letter.subject }}</h5>
            </div>
            <div class="sender flex-row flex-align-center">
                <div class="avatar">
                    <router-link v-bind:to="{ name: 'profile', params: { userId: letter.sender.id } }">
                        <img class="circular bordered-dark" v-bind:src="letter.sender.avatar" title="Avatar" />
                    </router-link>
                </div>
                <div>
                    <b>{{ letter.sender.name }} @ {{ letter.created }}</b></div>
            </div>
            <div class="content" v-html="letter.content"></div>
            <hr>
            <div class="right-content">
                <a style="float: left" class="img-btn" v-on:click="gotoMailbox"><i class="fas fa-arrow-left" title="Inbox"></i></a>
                <a class="img-btn" v-on:click="draftReply"><i class="fas fa-reply" title="Reply"></i></a>
                <a class="img-btn" v-on:click="deleteLetter"><i class="fas fa-trash" title="Delete"></i></a>
            </div>
        </div>
    `,
    data: function() {
        return {
            letter: null,
        }
    },
    methods: {
        gotoMailbox: function() {
            this.$router.push({ name: 'mail' });
        },
        draftReply: function() {
            this.$router.push({ name: 'reply', params: { letterId: this.letter.id } });
        },
        getLetter: function() {
            // fetching updates the local and remote letter.read property
            fetch(store.getters.getApiUrl+"/mail/"+this.letterId, {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("updateLetter", json);
                this.letter = json;
            });
        },
        deleteLetter: function() {
            fetch(store.getters.getApiUrl+"/mail/"+this.letter.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("updateMail", json.mail);
                this.$router.push({ name: "mail" });
                showFlash("Mail deleted.");
            });
        },
    },
    created: function() {
        this.getLetter();
    },
});

var Compose = Vue.component("compose", {
    template: `
        <div class="flex-width-10 flex-offset-1 flex-basis-10 mail">
            <div class="flex-column">
                <label for="receiver">To: *</label>
                <select name="receiver" v-model="letterForm.receiver">
                    <option value="" disabled selected>recipient...</option>
                    <option v-for="recipient in recipients" v-bind:key="recipient.id" v-bind:value="recipient.id">{{ recipient.name }}</option>
                </select>
                <label for="subject">Subject: *</label>
                <input name="subject" type="text" v-model="letterForm.subject" />
                <label for="content">Content: *</label>
                <textarea name="content" v-model="letterForm.content"></textarea>
                <hr>
                <div class="right-content">
                    <a class="img-btn" v-on:click="sendLetter"><i class="fas fa-paper-plane" title="Send"></i></a>
                    <a class="img-btn" v-on:click="discardDraft"><i class="fas fa-trash" title="Discard"></i></a>
                </div>
            </div>
        </div>
    `,
    data: function() {
        return {
            recipients: [],
            letterForm: {
                receiver: "",
                subject: "",
                content: "",
            },
        }
    },
    methods: {
        getUsers: function() {
            fetch(store.getters.getApiUrl+"/users", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.recipients = json.users.filter(function(user) {
                    var currentUser = JSON.parse(sessionStorage.getItem("userInfo"));
                    return user.id !== currentUser.id;
                });
            });
        },
        discardDraft: function() {
            router.go(-1);
        },
        sendLetter: function() {
            fetch(store.getters.getApiUrl+"/mail", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(this.letterForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => {
                // setting store.state.mail to an empty array
                // will cause the mail component to refetch
                store.dispatch("updateMail", []);
                this.$router.push({ name: "mail" });
                showFlash("Mail sent.");
            })
            .catch(error => {
                showFlash(error);
            });
        },
    },
    created: function() {
        this.getUsers();
    },
});

var Reply = Vue.component("reply", {
    props: {
        letterId: [Number, String],
    },
    template: `
        <div class="flex-width-10 flex-offset-1 flex-basis-10 mail">
            <div v-if="letter" class="flex-column">
                <div><h5>{{ letter.sender.name }}</h5></div>
                <input type="hidden" name="receiver" v-bind:value="letter.sender.id" />
                <label for="subject">Subject: *</label>
                <input name="subject" type="text" v-bind:value="'RE: '+letter.subject" />
                <label for="content">Content: *</label>
                <textarea name="content" v-model="letterForm.content" placeholder="Content here..."></textarea>
                <hr>
                <div class="right-content">
                    <a class="img-btn" v-on:click="sendReply"><i class="fas fa-paper-plane" title="Send"></i></a>
                    <a class="img-btn" v-on:click="discardDraft"><i class="fas fa-trash" title="Discard"></i></a>
                </div>
            </div>
        </div>
    `,
    data: function() {
        return {
            letter: null,
            letterForm: {
                content: "",
            },
        }
    },
    methods: {
        discardDraft: function() {
            router.go(-1);
        },
        getLetter: function() {
            this.letter = store.getters.getLetter(this.letterId);
        },
        sendReply: function() {
            fetch(store.getters.getApiUrl+"/mail", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify({
                    ...this.letterForm,
                    subject: "RE:"+this.letter.subject,
                    receiver: this.letter.sender.id,
                }),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => {
                store.dispatch("updateMail", []);
                this.$router.push({ name: "mail" });
                showFlash("Mail sent.");
            });
        },
    },
    created: function() {
        this.getLetter();
    },
});
