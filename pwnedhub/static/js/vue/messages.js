var Messages = Vue.component("messages", {
    template: `
        <div class="flex-grow">
            <create-message></create-message>
            <div class="messages flex-column">
                <show-message v-if="messages.length > 0" v-for="message in paginatedMessages" v-bind:key="message.id" v-bind:message="message"></show-message>
            </div>
            <pagination v-if="messages.length > 0" v-bind:pageNumber="pageNumber" v-bind:pageCount="pageCount" v-on:click="updatePageNumber"></pagination>
        </div>
    `,
    data: function() {
        return {
            pageNumber: 0,
            size: 5,
        }
    },
    computed: {
        messages: function() {
            return store.getters.getMessages;
        },
        paginatedMessages: function() {
            var start = this.pageNumber * this.size;
            var end = start + this.size;
            return store.getters.getMessages.slice(start, end);
        },
        pageCount: function() {
            var l = store.getters.getMessages.length
            var s = this.size;
            return Math.ceil(l/s);
        },
    },
    methods: {
        updatePageNumber: function(page) {
            this.pageNumber = page;
        }
    },
    beforeRouteEnter (to, from, next) {
        if (store.getters.getMessages.length > 0) {
            next();
        } else {
            fetch(store.getters.getApiUrl+"/messages", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("updateMessages", json.messages);
                next();
            })
            .catch(error => showFlash(error));
        }
    },
});

Vue.component("create-message", {
    template: `
        <div class="flex-row">
            <input class="flex-grow gutter-right" type="text" v-model="messageForm.message" placeholder="Message here..." />
            <input type="button" v-on:click="createMessage" value="Submit" />
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
        createMessage: function() {
            fetch(store.getters.getApiUrl+"/messages", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(this.messageForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("updateMessages", json.messages);
                Object.keys(this.messageForm).forEach((k) => {
                    this.messageForm[k] = "";
                });
            })
            .catch(error => showFlash(error));
        },
    },
});

Vue.component("show-message", {
    props: {
        message: Object,
    },
    template: `
            <div class="message flex-row">
                <a class="img-btn" v-if="isEditable(message) === true" v-on:click="deleteMessage(message)">
                    <i class="fas fa-trash" title="Delete"></i>
                </a>
                <div class="avatar">
                    <router-link v-bind:to="{ name: 'profile', params: { userId: message.author.id } }">
                        <img class="circular bordered-dark" v-bind:src="message.author.avatar" title="Avatar" />
                    </router-link>
                </div>
                <div v-bind:style="isAuthor(message) ? { fontWeight: 'bold' } : ''">
                    <p class="name"><span class="red">{{ message.author.name }}</span> <span style="font-size: .75em">({{ message.author.username }})</span></p>
                    <p class="comment" ref="message">{{ message.comment }}</p>
                    <scroll v-bind:message="message"></scroll>
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
            user = store.getters.getUserInfo;
            return (this.isAuthor(message) || user.role === "admin") ? true : false;
        },
        deleteMessage: function(message) {
            fetch(store.getters.getApiUrl+"/messages/"+message.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                store.dispatch("updateMessages", json.messages);
                showFlash("Message deleted.");
            })
            .catch(error => showFlash(error));
        },
    },
});

Vue.component("pagination", {
    props: {
        pageNumber: Number,
        pageCount: Number,
    },
    template: `
            <div class="pagination flex-row flex-align-center flex-justify-right">
                <a v-on:click="prevPage" v-bind:disabled="pageNumber === 0">&laquo;</a>
                <a v-for="(page, index) in pageCount" v-bind:key="page" v-on:click="gotoPage(index)" v-bind:class="pageNumber === index ? 'active' : ''">{{ index }}</a>
                <a v-on:click="nextPage" v-bind:disabled="pageNumber >= pageCount-1">&raquo;</a>
            </div>
    `,
    methods: {
        gotoPage: function(page) {
            this.$emit("click", page);
        },
        nextPage: function() {
            this.gotoPage(this.pageNumber+1);
        },
        prevPage: function() {
            this.gotoPage(this.pageNumber-1);
        },
    },
});

Vue.component("scroll", {
    props: {
        message: Object,
    },
    template: `
        <div class="scroll">
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
                    method: "POST",
                    body: JSON.stringify({url: url}),
                    headers:{"Content-Type": "application/json"}
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
                .catch(error => showFlash(error));
            }.bind(this));
        },
    },
    mounted: function() {
        this.doUnfurl(this.message);
    },
});
