var Messages = Vue.component("messages", {
    template: `
        <div class="flex-column flex-justify-end messages">
            <div id="message-container" class="message-container" v-chat-scroll="{ always: false, smooth: false, scrollonremoved: true }" @v-chat-scroll-top-reached="getNextPage">
                <message v-if="messages.length > 0" v-for="message in messages" v-bind:key="message.id" v-bind:message="message" v-on:delete="deleteMessage"></message>
            </div>
            <message-form v-on:create="createMessage"></message-form>
        </div>
    `,
    data: function() {
        return {
            messages: [],
            count: 0,
            pageNumber: 1,
        }
    },
    methods: {
        getMessages: function() {
            fetch(store.getters.getApiUrl+"/messages?page="+this.pageNumber, {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.messages.unshift(...json.messages);
                this.count = json.count;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        getNextPage: function() {
            if (this.messages.length < this.count) {
                this.pageNumber++;
                this.getMessages();
            }
        },
        createMessage: function(payload) {
            fetch(store.getters.getApiUrl+"/messages", {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(payload),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.messages.push(json)
            })
            .catch(error => store.dispatch("createToast", error));
        },
        deleteMessage: function(message) {
            fetch(store.getters.getApiUrl+"/messages/"+message.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => {
                this.messages.splice(this.messages.findIndex(m => m.id === message.id), 1);
            })
            .catch(error => {
                store.dispatch("createToast", error)
            });
        },
    },
    created: function() {
        this.getMessages();
    },
});

Vue.component("message-form", {
    template: `
        <div class="flex-row flex-align-center message-form">
            <input class="flex-grow" type="text" v-model="messageForm.message" v-on:keyup="handleKeyPress" placeholder="Message here..." />
            <button class="show" v-on:click="createMessage"><i class="fas fa-paper-plane" title="Send"></i></button>
        </div>
    `,
    data: function() {
        return {
            messageForm: {
                message: "",
            },
        }
    },
    methods: {
        handleKeyPress: function(event) {
            if (event.keyCode === 13) {
                this.createMessage();
            }
        },
        createMessage: function() {
            if (this.messageForm.message) {
                this.$emit('create', this.messageForm);
                this.messageForm.message = "";
            }
        },
    },
});

Vue.component("message", {
    props: {
        message: Object,
    },
    template: `
            <div class="flex-row message">
                <a class="img-btn" v-if="isEditable(message) === true" v-on:click="deleteMessage(message)">
                    <i class="fas fa-trash" title="Delete"></i>
                </a>
                <div class="avatar">
                    <router-link v-bind:to="{ name: 'profile', params: { userId: message.author.id } }">
                        <img class="circular bordered-dark" v-bind:src="message.author.avatar" title="Avatar" />
                    </router-link>
                </div>
                <div>
                    <p class="name">{{ message.author.name }}</span> <span style="font-size: .75em">({{ message.author.username }})</span></p>
                    <p class="comment" ref="message">{{ message.comment }}</p>
                    <link-preview v-bind:message="message"></link-preview>
                    <p class="timestamp">{{ message.created }}</p>
                </div>
            </div>
    `,
    methods: {
        isAuthor: function(message) {
            user = store.getters.getUserInfo;
            return (user.id === message.author.id) ? true : false;
        },
        isEditable: function(message) {
            return (this.isAuthor(message) || store.getters.isAdmin) ? true : false;
        },
        deleteMessage: function(message) {
            this.$emit('delete', message);
        },
    },
});

Vue.component("link-preview", {
    props: {
        message: Object,
    },
    template: `
        <div class="link-preview">
            <a v-for="(unfurl, index) in unfurls" v-bind:key="index" v-bind:unfurl="unfurl" v-bind:href="unfurl.url">
                <p>{{ unfurl.values.join(" | ") }}</p>
            </a>
        </div>
    `,
    data: function() {
        return {
            unfurls: [],
        }
    },
    methods: {
        parseUrls: function(message) {
            var pattern = /\w+:\/\/[^\s]+/gi;
            var matches = message.comment.match(pattern);
            return matches || [];
        },
        doUnfurl: function(message) {
            var urls = this.parseUrls(message);
            urls.forEach(function(value, key) {
                // remove punctuation from URLs ending a sentence
                var url = value.replace(/[!.?]+$/g, '');
                fetch(store.getters.getApiUrl+"/unfurl", {
                    credentials: "include",
                    headers: {"Content-Type": "application/json"},
                    method: "POST",
                    body: JSON.stringify({url: url}),
                })
                .then(handleErrors)
                .then(response => response.json())
                .then(json => {
                    var unfurl = Object;
                    unfurl.url = json.url;
                    unfurl.values = [];
                    var keys = ["site_name", "title", "description"];
                    for (var k in keys) {
                        if (json[keys[k]] !== null) {
                            unfurl.values.push(json[keys[k]]);
                        }
                    }
                    if (unfurl.values.length > 0) {
                        this.unfurls.push(unfurl);
                    }
                })
                .catch(error => {});
            }.bind(this));
        },
    },
    mounted: function() {
        this.doUnfurl(this.message);
    },
});
