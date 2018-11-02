var Messages = Vue.component("messages", {
    template: `
        <div>
            <div class="row">
                <div class="ten columns offset-by-one center-content">
                    <create-message v-on:click="updateMessages"></create-message>
                </div>
            </div>
            <div class="row">
                <div class="ten columns offset-by-one messages">
                    <show-messages v-on:click="updateMessages" v-bind:messages="messages"></show-messages>
                </div>
            </div>
        </div>
    `,
    data: function() {
        return {
            messages: [],
        }
    },
    methods: {
        getUserInfo: function() {
            fetch(this.URL_API_USER_READ)
            .then(response => response.json())
            .then(json => {
                window.sessionStorage.setItem("userInfo", JSON.stringify(json));
            });
        },
        updateMessages: function(messages) {
            this.messages = messages;
        },
        getMessages: function(event) {
            fetch(this.URL_API_MESSAGES_READ)
            .then(response => response.json())
            .then(json => {
                this.updateMessages(json.messages);
            });
        },
    },
    created: function() {
        this.getUserInfo();
        this.getMessages();
    },
    mounted: function() {
        // poll for messages
        /*setInterval(function () {
            this.getMessages();
        }.bind(this), 30*1000);*/
    },
});

Vue.component("create-message", {
    template: `
        <div>
            <form v-on:submit.prevent="createMessage">
                <button style="float: right;" type="submit">submit</button>
                <span style="display: block; overflow: hidden; padding-right: 10px">
                    <input type="text" v-model="messageForm.message" style="width: 100%;" placeholder="message here..." />
                </span>
            </form>
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
        createMessage: function(event) {
            fetch(this.URL_API_MESSAGE_CREATE, {
                method: "POST",
                body: JSON.stringify(this.messageForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(response => response.json())
            .then(json => {
                // update messages with the response
                this.$emit("click", json.messages);
                // reset the form
                Object.keys(this.messageForm).forEach((k) => {
                    this.messageForm[k] = "";
                });
            })
        },
    },
});

Vue.component("show-messages", {
    props: {
        messages: Array,
    },
    template: `
        <div>
            <div class="center-content" v-if="messages.length === 0">
                no messages
            </div>
            <div v-else v-for="message in paginatedMessages" v-bind:key="message.id" v-bind:message="message">
                <div v-if="isEditable(message) === true" v-bind:name="'action_'+message.id" class="delete">
                    <a v-on:click="deleteMessage(message)">
                        <img v-bind:src="URL_IMG_TRASH" />
                    </a>
                </div>
                <div v-bind:style="isAuthor(message) ? { fontWeight: 'bold' } : ''">
                    <p class="name"><span class="red">{{ message.author.name }}</span> <span style="font-size: .75em">({{ message.author.username }})</span></p>
                    <p class="message" ref="message">{{ message.comment }}</p>
                    <scroll v-bind:message="message"></scroll>
                    <p class="timestamp">{{ message.created }}</p>
                </div>
            </div>
            <div class="pagination">
                <span v-on:click="prevPage" v-bind:disabled="pageNumber === 0">prev</span>
                |
                <span v-on:click="nextPage" v-bind:disabled="pageNumber >= pageCount-1">next</span>
            </div>
        </div>
    `,
    data: function() {
        return {
            pageNumber: 0,
            size: 5,
        }
    },
    methods: {
        nextPage: function() {
            this.pageNumber++;
        },
        prevPage: function() {
            this.pageNumber--;
        },
        isAuthor: function(message) {
            user = JSON.parse(window.sessionStorage.getItem("userInfo"));
            return (user.id === message.author.id) ? true : false;
        },
        isEditable: function(message) {
            user = JSON.parse(window.sessionStorage.getItem("userInfo"));
            return (this.isAuthor(message) || user.role === "admin") ? true : false;
        },
        deleteMessage: function(message) {
            fetch(this.URL_API_MESSAGE_DELETE.format(message.id), {
                method: "DELETE",
            })
            .then(response => response.json())
            .then(json => {
                // update messages with the response
                this.$emit("click", json.messages);
                // must use the global flash function as the
                // flash div is outside the Vue app anchor
                show_flash("Message deleted.");
            });
        },
    },
    computed: {
        pageCount: function() {
            let l = this.messages.length
            let s = this.size;
            return Math.ceil(l/s);
        },
        paginatedMessages: function() {
            const start = this.pageNumber * this.size;
            const end = start + this.size;
            return this.messages.slice(start, end);
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
                <p>{{ unfurl.site_name }} | {{ unfurl.title }} | {{ unfurl.description }}</p>
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
            var pattern = /\w+:(\/?\/?)[^\s]+/gi;
            matches = message.comment.match(pattern);
            return matches || [];
        },
        doUnfurl: function(message) {
            var urls = this.parseUrls(message);
            urls.forEach(function(value, key) {
                fetch(this.URL_API_UNFURL, {
                    method: "POST",
                    body: JSON.stringify({url: value}),
                    headers:{"Content-Type": "application/json"}
                })
                .then(response => response.json())
                .then(json => {
                    this.unfurls.push(json);
                })
            }.bind(this));
        },
    },
    mounted: function() {
        this.doUnfurl(this.message);
    },
});
