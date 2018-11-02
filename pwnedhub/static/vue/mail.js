var Mail = Vue.component("mail", {
    template: `
        <div class="row">
            <div class="ten columns offset-by-one">
                <input type="button" onclick="" value="compose" />
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
                <input type="button" value="view" v-on:click="openEnvelope" />
                <input type="button" value="reply" onclick="" />
                <input type="button" value="delete" v-on:click="deleteEnvelope" />
            </td>
        </tr>
    `,
    methods: {
        openEnvelope: function() {
            this.$router.push({ name: 'Letter', params: { envelopeId: this.envelope.id } });
        },
        deleteEnvelope: function() {
            fetch(this.URL_API_MAIL_DELETE.format(this.envelope.id), {
                method: "DELETE",
            })
            .then(response => response.json())
            .then(json => {
                this.$emit("click", json.mail);
            });
        },
    },
});

var Letter = Vue.component("letter", {
    props: {
        envelopeId: Number,
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
                    <input type="button" value="inbox" v-on:click="gotoMailbox" />
                    <input type="button" value="reply" onclick="" />
                    <input type="button" value="delete" v-on:click="deleteEnvelope" />
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
            .then(response => response.json())
            .then(json => {
                this.$router.push({ name: "Mail" });
            });
        },
    },
    created: function() {
        this.getEnvelope();
    },
});
