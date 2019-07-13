var Messages = Vue.component("messages", {
    template: `
        <div class="flex-grow">
            <create-message v-on:click="updateMessages"></create-message>
            <show-messages v-on:click="updateMessages" v-bind:messages="messages"></show-messages>
        </div>
    `,
    data: function() {
        return {
            messages: [],
        }
    },
    methods: {
        updateMessages: function(messages) {
            this.messages = messages;
        },
        getMessages: function() {
            fetch(this.URL_API_BASE+"/messages", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.updateMessages(json.messages);
            });
        },
    },
    created: function() {
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
        <form class="flex-width-10 flex-offset-1 flex-row flex-align-center" v-on:submit.prevent="createMessage">
            <input class="flex-grow gutter-right" type="text" v-model="messageForm.message" placeholder="Message here..." />
            <input type="submit" value="Submit" />
        </form>
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
            fetch(this.URL_API_BASE+"/messages", {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(this.messageForm),
                headers:{"Content-Type": "application/json"}
            })
            .then(handleErrors)
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
        <div class="messages flex-column">
            <div class="message flex-row" v-if="messages.length > 0" v-for="message in paginatedMessages" v-bind:key="message.id" v-bind:message="message">
                <a class="img-btn" v-if="isEditable(message) === true" v-on:click="deleteMessage(message)">
                    <i class="fas fa-trash" title="Delete"></i>
                </a>
                <div class="avatar">
                    <a href="#">
                        <img class="circular bordered-dark" v-bind:src="message.author.avatar" title="Avatar" />
                    </a>
                </div>
                <div v-bind:style="isAuthor(message) ? { fontWeight: 'bold' } : ''">
                    <p class="name"><span class="red">{{ message.author.name }}</span> <span style="font-size: .75em">({{ message.author.username }})</span></p>
                    <p class="comment" ref="message">{{ message.comment }}</p>
                    <scroll v-bind:message="message"></scroll>
                    <p class="timestamp">{{ message.created }}</p>
                </div>
            </div>
            <div class="pagination flex-row flex-align-center flex-justify-right" v-if="messages.length > 0" >
                <a v-on:click="prevPage" v-bind:disabled="pageNumber === 0">&laquo;</a>
                <a v-for="(page, index) in pageCount" v-bind:key="page" v-on:click="gotoPage(index)" v-bind:class="pageNumber === index ? 'active' : ''">{{ index }}</a>
                <a v-on:click="nextPage" v-bind:disabled="pageNumber >= pageCount-1">&raquo;</a>
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
        gotoPage: function(page) {
            this.pageNumber = page;
        },
        isAuthor: function(message) {
            user = JSON.parse(sessionStorage.getItem("userInfo"));
            return (user.id === message.author.id) ? true : false;
        },
        isEditable: function(message) {
            user = JSON.parse(sessionStorage.getItem("userInfo"));
            return (this.isAuthor(message) || user.role === "admin") ? true : false;
        },
        deleteMessage: function(message) {
            fetch(this.URL_API_BASE+"/messages/"+message.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
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
                fetch(this.URL_API_BASE+"/unfurl", {
                    credentials: "include",
                    method: "POST",
                    body: JSON.stringify({url: value}),
                    headers:{"Content-Type": "application/json"}
                })
                .then(handleErrors)
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
