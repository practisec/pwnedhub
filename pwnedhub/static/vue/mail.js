var Mail = Vue.component("mail", {
    template: `
        <div class="row">
            <div class="ten columns offset-by-one">
                <input type="button" value="Compose" v-on:click="draftLetter" />
                <div class="inbox">
                    <table class="u-full-width center">
                        <thead>
                            <tr>
                                <th class="left-content">from</th>
                                <th class="left-content">subject</th>
                                <th>date</th>
                                <th>action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="mail.length === 0">
                                <td colspan="4" class="center-content">you have no mail</td>
                            </tr>
                            <envelope v-else v-for="envelope in mail" v-bind:key="envelope.id" v-bind:envelope="envelope" v-on:click="updateMail"></envelope>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `,
    data: function() {
        return {
            mail: [],
        }
    },
    methods: {
        draftLetter: function() {
            this.$router.push({ name: 'Compose' });
        },
        updateMail: function(mail) {
            this.mail = mail;
        },
        getMail: function() {
            fetch(this.URL_API_MAILBOX_READ)
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
        <tr v-bind:style="!envelope.read ? { fontWeight: 'bold' } : ''">
            <td class="left-content">{{ envelope.sender.name }}</td>
            <td class="left-content">{{ envelope.subject }}</td>
            <td>{{ envelope.created }}</td>
            <td>
                <button type="button" class="img-btn" v-on:click="openEnvelope"><img v-bind:src="URL_IMG_VIEW" title="View" /></button>
                <button type="button" class="img-btn" v-on:click="draftReply"><img v-bind:src="URL_IMG_REPLY" title="Reply" /></button>
                <button type="button" class="img-btn" v-on:click="deleteEnvelope"><img v-bind:src="URL_IMG_DELETE" title="Delete" /></button>
            </td>
        </tr>
    `,
    methods: {
        openEnvelope: function() {
            this.$router.push({ name: 'Letter', params: { envelopeId: this.envelope.id } });
        },
        draftReply: function() {
            this.$router.push({ name: 'Reply', params: { letterId: this.envelope.id } });
        },
        deleteEnvelope: function() {
            fetch(this.URL_API_MAIL_DELETE.format(this.envelope.id), {
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.$emit("click", json.mail);
                showFlash("Mail deleted.");
            });
        },
    },
});

var Letter = Vue.component("letter", {
    props: {
        envelopeId: [Number, String],
    },
    template: `
        <div class="row">
            <div v-if="envelope" class="ten columns offset-by-one mail">
                <label for="sender">From:</label>
                <div class="u-full-width" name="sender">{{ envelope.sender.name }}</div><br>
                <label for="subject">Subject:</label>
                <div class="u-full-width" name="subject"><h5>{{ envelope.subject }}</h5></div>
                <label for="content">Content:</label>
                <div class="u-full-width bordered rounded" name="content">{{ envelope.content }}</div><br>
                <div class="u-full-width right-content">
                    <button type="button" class="img-btn" v-on:click="gotoMailbox"><img v-bind:src="URL_IMG_INBOX" title="Inbox" /></button>
                    <button type="button" class="img-btn" v-on:click="draftReply"><img v-bind:src="URL_IMG_REPLY" title="Reply" /></button>
                    <button type="button" class="img-btn" v-on:click="deleteEnvelope"><img v-bind:src="URL_IMG_DELETE" title="Delete" /></button>
                </div>
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
            this.$router.push({ name: 'Mail' });
        },
        draftReply: function() {
            this.$router.push({ name: 'Reply', params: { letterId: this.envelope.id } });
        },
        getEnvelope: function() {
            fetch(this.URL_API_MAIL_READ.format(this.envelopeId))
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.envelope = json;
            });
        },
        deleteEnvelope: function() {
            fetch(this.URL_API_MAIL_DELETE.format(this.envelope.id), {
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => {
                this.$router.push({ name: "Mail" });
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
        <div class="row">
            <div class="ten columns offset-by-one mail">
                <label for="receiver">To:</label>
                <select name="receiver" v-model="letterForm.receiver">
                    <option value="" disabled hidden>recipient...</option>
                    <option v-for="recipient in recipients" v-bind:key="recipient.id" v-bind:value="recipient.id">{{ recipient.name }}</option>
                </select><br>
                <label for="subject">Subject:</label>
                <input class="u-full-width" name="subject" type="text" v-model="letterForm.subject" placeholder="Subject here..." /><br>
                <label for="content">Content:</label>
                <textarea class="u-full-width" name="content" v-model="letterForm.content" placeholder="Content here..."></textarea><br>
                <div class="u-full-width right-content">
                    <button type="button" class="img-btn" v-on:click="sendLetter"><img v-bind:src="URL_IMG_SEND" title="Send" /></button>
                    <button type="button" class="img-btn" v-on:click="discardDraft"><img v-bind:src="URL_IMG_DELETE" title="Discard" /></button>
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
            fetch(this.URL_API_USERS_READ)
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
            fetch(this.URL_API_MAIL_CREATE, {
                method: "POST",
                body: JSON.stringify(this.letterForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => {
                this.$router.push({ name: "Mail" });
                showFlash("Mail sent.");
            })
            .catch(error => {
                showFlash("Error sending mail.");
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
        <div class="row">
            <div v-if="letter" class="ten columns offset-by-one mail">
                <label for="receiver-show">To:</label>
                <div class="u-full-width" name="receiver-show">{{ letter.sender.name }}</div><br>
                <label for="subject-show">Subject:</label>
                <div class="u-full-width" name="subject-show"><h5>RE: {{ letter.subject }}</h5></div>
                <label for="content">Content:</label>
                <textarea class="u-full-width" name="content" v-model="letterForm.content" placeholder="Content here..."></textarea><br>
                <div class="u-full-width right-content">
                    <button type="button" class="img-btn" v-on:click="sendReply"><img v-bind:src="URL_IMG_SEND" title="Send" /></button>
                    <button type="button" class="img-btn" v-on:click="discardDraft"><img v-bind:src="URL_IMG_DELETE" title="Discard" /></button>
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
            fetch(this.URL_API_MAIL_READ.format(this.letterId))
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.letter = json;
            });
        },
        sendReply: function() {
            fetch(this.URL_API_MAIL_CREATE, {
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
                this.$router.push({ name: "Mail" });
                showFlash("Mail sent.");
            });
        },
    },
    created: function() {
        this.getLetter();
    },
});
