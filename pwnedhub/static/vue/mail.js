var Mail = Vue.component("mail", {
    template: `
        <div class="row">
            <div class="ten columns offset-by-one">
                <input type="button" value="compose" v-on:click="draftLetter" />
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
                <button type="button" class="img-btn" v-on:click="openEnvelope"><img v-bind:src="URL_IMG_VIEW" title="view" /></button>
                <button type="button" class="img-btn" v-on:click="draftReply"><img v-bind:src="URL_IMG_REPLY" title="reply" /></button>
                <button type="button" class="img-btn" v-on:click="deleteEnvelope"><img v-bind:src="URL_IMG_DELETE" title="delete" /></button>
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
            .then(response => response.json())
            .then(json => {
                this.$emit("click", json.mail);
                show_flash("Mail deleted.");
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
                <label for="sender">from:</label>
                <div class="u-full-width" name="sender">{{ envelope.sender.name }}</div><br>
                <label for="subject">subject:</label>
                <div class="u-full-width" name="subject"><h5>{{ envelope.subject }}</h5></div>
                <label for="content">content:</label>
                <div class="u-full-width bordered rounded" name="content">{{ envelope.content }}</div><br>
                <div class="u-full-width right-content">
                    <button type="button" class="img-btn" v-on:click="gotoMailbox"><img v-bind:src="URL_IMG_INBOX" title="inbox" /></button>
                    <button type="button" class="img-btn" v-on:click="draftReply"><img v-bind:src="URL_IMG_REPLY" title="reply" /></button>
                    <button type="button" class="img-btn" v-on:click="deleteEnvelope"><img v-bind:src="URL_IMG_DELETE" title="delete" /></button>
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
            .then(response => response.json())
            .then(json => {
                this.envelope = json;
            });
        },
        deleteEnvelope: function() {
            fetch(this.URL_API_MAIL_DELETE.format(this.envelope.id), {
                method: "DELETE",
            })
            .then(response => {
                this.$router.push({ name: "Mail" });
                show_flash("Mail deleted.");
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
                <label for="receiver">to:</label>
                <select name="receiver" v-model="letterForm.receiver">
                    <option value="" disabled hidden>recipient...</option>
                    <option v-for="recipient in recipients" v-bind:key="recipient.id" v-bind:value="recipient.id">{{ recipient.name }}</option>
                </select><br>
                <label for="subject">subject:</label>
                <input class="u-full-width" name="subject" type="text" v-model="letterForm.subject" placeholder="subject here..." /><br>
                <label for="content">content:</label>
                <textarea class="u-full-width" name="content" v-model="letterForm.content" placeholder="content here..."></textarea><br>
                <div class="u-full-width right-content">
                    <button type="button" class="img-btn" v-on:click="sendLetter"><img v-bind:src="URL_IMG_SEND" title="send" /></button>
                    <button type="button" class="img-btn" v-on:click="discardDraft"><img v-bind:src="URL_IMG_DELETE" title="discard" /></button>
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
            .then(response => response.json())
            .then(json => {
                this.recipients = json.users.filter(function(user) {
                    var currentUser = JSON.parse(window.sessionStorage.getItem("userInfo"));
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
                show_flash("Mail sent.");
            })
            .catch(error => {
                show_flash("Error sending mail.");
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
                <label for="receiver-show">to:</label>
                <div class="u-full-width" name="receiver-show">{{ letter.sender.name }}</div><br>
                <label for="subject-show">subject:</label>
                <div class="u-full-width" name="subject-show"><h5>RE: {{ letter.subject }}</h5></div>
                <label for="content">content:</label>
                <textarea class="u-full-width" name="content" v-model="letterForm.content" placeholder="content here..."></textarea><br>
                <div class="u-full-width right-content">
                    <button type="button" class="img-btn" v-on:click="sendReply"><img v-bind:src="URL_IMG_SEND" title="send" /></button>
                    <button type="button" class="img-btn" v-on:click="discardDraft"><img v-bind:src="URL_IMG_DELETE" title="discard" /></button>
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
            .then(response => {
                this.$router.push({ name: "Mail" });
                show_flash("Mail sent.");
            });
        },
    },
    created: function() {
        this.getLetter();
    },
});
