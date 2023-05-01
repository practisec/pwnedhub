var Messaging = Vue.component("messaging", {
    template: `
        <div class="flex-row messaging">
            <rooms v-bind:users="users" v-bind:rooms="rooms" v-bind:selectedRoom="room" v-bind:taggedRooms="taggedRooms" v-on:load="loadRoom"></rooms>
            <messages v-if="room.id" v-bind:room="room" v-on:tag="tagRoom"></messages>
        </div>
    `,
    data: function() {
        return {
            users: [],
            rooms: [],
            room: {},
            taggedRooms: [],
        }
    },
    methods: {
        loadRoom: function(room) {
            this.room = room;
            this.untagRoom(room);
            console.log(`Loaded room: id=${room.id}, name=${room.name}`);
        },
        untagRoom: function(room) {
            var index = this.taggedRooms.findIndex(r => r.id === room.id)
            if (index !== -1) {
                this.taggedRooms.splice(index, 1);
            }
        },
        tagRoom: function(room) {
            var index = this.taggedRooms.findIndex(r => r.id === room.id)
            if (index === -1) {
                this.taggedRooms.push(room);
            }
        },
    },
    sockets: {
        log(data) {
            console.log(data);
        },
        loadUsers(data) {
            this.users = data.users.filter(user => user.id != store.getters.getUserInfo.id);
            console.log("Users preloaded.");
        },
        loadRooms(data) {
            data.rooms.forEach(room => {
                if (!this.rooms.find(e => e.id === room.id)) {
                    this.rooms.push(room);
                    console.log(`Preloaded room: id=${room.id}, name=${room.name}`);
                    this.$socket.client.emit("join-room", room);
                }
            })
        },
        loadRoom(data) {
            this.loadRoom(data);
        },
    },
    created: function() {
        // if using Bearer authentication, send the auth token as query string
        // socketio doesn't support custom headers for websocket transports
        if (store.getters.getAuthHeader.hasOwnProperty("Authorization")) {
            this.$socket.client.io.opts.query.access_token = store.getters.getAuthHeader.Authorization.split(" ")[1];
        }
        this.$socket.client.open();
    },
    beforeDestroy: function() {
        this.$socket.client.close();
        console.log("Socket disconnected.");
    },
});

Vue.component("rooms", {
    props: {
        rooms: Array,
        users: Array,
        selectedRoom: Object,
        taggedRooms: Array,
    },
    template: `
        <div class="rooms">
            <div class="tab" v-bind:class="{closed: !menuOpen}" v-on:click="toggleMenu"></div>
            <div class="flex-column rooms-wrapper"" v-bind:class="{closed: !menuOpen}">
                <div>
                    <div class="label">Rooms</div>
                    <div class="room" v-for="room in rooms" v-bind:key="'room-'+room.id" v-bind:room="room" v-on:click.stop="loadRoom(room)" v-bind:class="{ active: isSelected(room), tagged: isTagged(room) }">{{ room.display }}</div>
                </div>
                <div>
                    <div class="label">Users</div>
                    <div class="room" v-for="user in users" v-bind:key="'user-'+user.id" v-bind:user="user" v-on:click.stop="createRoom(user)">{{ user.name }}</div>
                </div>
            </div>
        </div>
    `,
    data: function() {
        return {
            menuOpen: false,
        }
    },
    methods: {
        isSelected: function(room) {
            return room.id === this.selectedRoom.id
        },
        isTagged: function(room) {
            return (this.taggedRooms.findIndex(r => r.id === room.id) !== -1) ? true : false;
        },
        toggleMenu: function() {
            this.menuOpen = !this.menuOpen;
        },
        loadRoom: function(room) {
            this.menuOpen = false;
            this.$emit("load", room);
        },
        createRoom: function(user) {
            var ids = [store.getters.getUserInfo.id, user.id].sort();
            var name = ids.join(':');
            var room = {name: name, private: true, members: ids}
            this.$socket.client.emit("create-room", room);
        },
    },
});

Vue.component("messages", {
    props: {
        room: Object,
    },
    template: `
        <div class="flex-grow flex-column flex-justify-end messages">
            <div id="message-container" class="message-container" ref="container">
                <infinite-loading spinner="spiral" v-bind:identifier="infiniteId" v-bind:distance="0" direction="top" v-on:infinite="infiniteHandler">
                    <span slot="no-results"></span>
                </infinite-loading>
                <message v-if="messages.length > 0" v-for="message in messages" v-bind:key="message.id" v-bind:message="message" v-on:delete="deleteMessage"></message>
            </div>
            <message-form v-bind:room="room" v-on:create="createMessage"></message-form>
        </div>
    `,
    data: function() {
        return {
            messages: [],
            cursor: null,
            infiniteId: null,
        }
    },
    watch: {
        room: function() {
            this.messages = [];
            this.cursor = null;
            this.infiniteId = this.room.id;
        }
    },
    methods: {
        scrollToEnd: function() {
            var content = this.$refs.container;
            content.scrollTop = content.scrollHeight;
        },
        infiniteHandler($state) {
            this.getMessages($state);
        },
        getMessages: function($state) {
            var query = "";
            if (this.cursor) {
                query = "?cursor="+this.cursor;
            }
            fetch(store.getters.getApiUrl+"/rooms/"+this.room.id+"/messages"+query, {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.cursor = json.cursor;
                // prepend messages with the older messages
                this.messages.unshift(...json.messages);
                if (json.next) {
                    $state.loaded();
                } else {
                    $state.complete()
                }
            })
            .catch(error => store.dispatch("createToast", error));
        },
        createMessage: function(message) {
            this.$socket.client.emit("create-message", {message: message, room: this.room});
        },
        deleteMessage: function(message) {
            this.$socket.client.emit("delete-message", {message: message, room: this.room});
        },
    },
    sockets: {
        newMessage(message) {
            if (message.room.id === this.room.id) {
                this.messages.push(message);
                this.$nextTick(function () {
                    this.scrollToEnd();
                });
            } else {
                this.$emit("tag", message.room);
            }
        },
        delMessage(message) {
            if (message.room.id === this.room.id) {
                var index = this.messages.findIndex(m => m.id === message.id)
                if (index !== -1) {
                    this.messages.splice(index, 1);
                }
            }
        },
    },
});

Vue.component("message-form", {
    props: {
        room: Object,
    },
    template: `
        <div class="flex-row flex-align-center message-form">
            <input class="flex-grow" type="text" v-model="messageForm.comment" v-on:keyup="handleKeyPress" v-bind:placeholder="'Message '+room.display" />
            <button class="show" v-on:click="createMessage"><i class="fas fa-paper-plane" title="Send"></i></button>
        </div>
    `,
    data: function() {
        return {
            messageForm: {
                comment: "",
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
            if (this.messageForm.comment) {
                this.$emit("create", this.messageForm);
                this.messageForm.comment = "";
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
