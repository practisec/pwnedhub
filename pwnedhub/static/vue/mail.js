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
                    <envelope v-if="mail.length > 0" v-for="envelope in mail" v-bind:key="envelope.id" v-bind:envelope="envelope" v-on:click="updateMail"></envelope>
                    <tr v-else>
                        <td colspan="4" class="center-content"><i class="fas fa-exclamation-circle medium" title="Empty"></i></td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    data: function() {
        return {
            mail: [],
        }
    },
    methods: {
        draftLetter: function() {
            this.$router.push({ name: 'compose' });
        },
        updateMail: function(mail) {
            this.mail = mail;
        },
        getMail: function() {
            fetch(this.URL_API_BASE+"/mail", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.updateMail(json.mail);
            });
        },
    },
    created: function() {
        this.getMail();
    },
});

Vue.component("envelope", {
    props: {
        envelope: Object,
    },
    template: `
        <tr v-bind:style="!envelope.read ? { fontWeight: 'bold' } : ''" v-on:click="openEnvelope">
            <td class="left-content">{{ envelope.sender.name }}</td>
            <td class="left-content">{{ envelope.subject }}</td>
            <td>{{ envelope.created }}</td>
        </tr>
    `,
    methods: {
        openEnvelope: function() {
            this.$router.push({ name: 'letter', params: { envelopeId: this.envelope.id } });
        },
    },
});

var Letter = Vue.component("letter", {
    props: {
        envelopeId: [Number, String],
    },
    template: `
        <div v-if="envelope" class="flex-width-10 flex-offset-1 flex-basis-10 mail">
            <div>
                <h5>{{ envelope.subject }}</h5>
            </div>
            <div class="sender flex-row flex-align-center">
                <div class="avatar">
                    <router-link v-bind:to="{ name: 'profile', params: { userId: envelope.sender.id } }">
                        <img class="circular bordered-dark" v-bind:src="envelope.sender.avatar" title="Avatar" />
                    </router-link>
                </div>
                <div>
                    <b>{{ envelope.sender.name }} @ {{ envelope.created }}</b></div>
            </div>
            <div class="content" v-html="envelope.content"></div>
            <hr>
            <div class="right-content">
                <a style="float: left" class="img-btn" v-on:click="gotoMailbox"><i class="fas fa-arrow-left" title="Inbox"></i></a>
                <a class="img-btn" v-on:click="draftReply"><i class="fas fa-reply" title="Reply"></i></a>
                <a class="img-btn" v-on:click="deleteEnvelope"><i class="fas fa-trash" title="Delete"></i></a>
            </div>
        </div>
    `,
    data: function() {
        return {
            envelope: null,
        }
    },
    methods: {
        gotoMailbox: function() {
            this.$router.push({ name: 'mail' });
        },
        draftReply: function() {
            this.$router.push({ name: 'reply', params: { letterId: this.envelope.id } });
        },
        getEnvelope: function() {
            fetch(this.URL_API_BASE+"/mail/"+this.envelopeId, {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.envelope = json;
            });
        },
        deleteEnvelope: function() {
            fetch(this.URL_API_BASE+"/mail/"+this.envelope.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => {
                this.$router.push({ name: "mail" });
                showFlash("Mail deleted.");
            });
        },
    },
    created: function() {
        this.getEnvelope();
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
            fetch(this.URL_API_BASE+"/users", {
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
            fetch(this.URL_API_BASE+"/mail", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(this.letterForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => {
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
            fetch(this.URL_API_BASE+"/mail/"+this.letterId, {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.letter = json;
            });
        },
        sendReply: function() {
            fetch(this.URL_API_BASE+"/mail", {
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
                this.$router.push({ name: "mail" });
                showFlash("Mail sent.");
            });
        },
    },
    created: function() {
        this.getLetter();
    },
});
