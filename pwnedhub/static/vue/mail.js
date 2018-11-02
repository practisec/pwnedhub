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
                            <envelope v-else v-for="envelope in mail" v-bind:key="envelope.id" v-bind:envelope="envelope"></envelope>
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
            // [vuln] api returns all data and relies on client-side authz
            fetch(this.URL_API_MAIL_GET)
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
                <router-link tag="button" v-bind:to="{ name: 'Letter', params: { envelopeId: envelope.id }}">view</router-link>
                <input type="button" value="reply" onclick="" />
                <input type="button" value="delete" onclick="" />
            </td>
        </tr>
    `,
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
                    <router-link tag="button" v-bind:to="{ name: 'Mail' }">inbox</router-link>
                    <input type="button" value="reply" onclick="" />
                    <input type="button" value="delete" onclick="" />
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
        getEnvelope: function() {
            fetch(this.URL_API_LETTER_GET.format(this.envelopeId))
            .then(response => response.json())
            .then(json => {
                this.envelope = json;
            });
        },
    },
    created: function() {
        this.getEnvelope();
    },
});
