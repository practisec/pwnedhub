import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';
import { Message } from '../services/api.js';
import { socket } from '../helpers/socket.js';
import LinkPreview from '../components/link-preview.js';

const { ref, computed, watch, nextTick, onBeforeUnmount } = Vue;

const template = `
<div class="flex-row messaging">
    <div class="rooms">
        <div class="tab" :class="{closed: !menuOpen}" @click="toggleMenu"></div>
        <div class="flex-column rooms-wrapper" :class="{closed: !menuOpen}">
            <div v-if="channels.length > 0">
                <div class="label">Channels</div>
                <div class="room" v-for="room in channels" :id="room.id" :key="'channel-'+room.id" :room="room" @click.stop="loadRoom(room)" :class="{ active: isSelected(room), tagged: isTagged(room) }">#{{ room.name }}</div>
            </div>
            <div v-if="directs.length > 0">
                <div class="label">Directs</div>
                <div class="room" v-for="room in directs" :id="room.id" :key="'channel-'+room.id" :room="room" @click.stop="loadRoom(room)" :class="{ active: isSelected(room), tagged: isTagged(room) }">@{{ room.peer.name }}</div>
            </div>
            <div v-if="filteredUsers.length > 0">
                <div class="label">Users</div>
                <div class="room" v-for="user in filteredUsers" :key="'user-'+user.id" :user="user" @click.stop="createRoom(user)">{{ user.name }}</div>
            </div>
        </div>
    </div>
    <div class="flex-grow flex-column flex-justify-end messages">
        <div id="message-container" class="message-container" ref="scrollContainer">
            <infinite-loading target="#message-container" :top="true" :identifier="infiniteId" :firstload="false" @infinite="infiniteHandler">
                <template #complete>
                    <span></span>
                </template>
            </infinite-loading>
            <div v-for="message in messages" v-bind:key="message.id" v-bind:message="message" class="flex-row message">
                <a class="img-btn" v-if="isEditable(message) === true" @click="deleteMessage(message)">
                    <i class="fas fa-trash" title="Delete"></i>
                </a>
                <div class="avatar">
                    <router-link :to="{ name: 'profile', params: { userId: message.author.id } }">
                        <img class="circular bordered-dark" :src="message.author.avatar" title="Avatar" />
                    </router-link>
                </div>
                <div>
                    <p class="name">{{ message.author.name }}</p>
                    <p class="comment">{{ message.comment }}</p>
                    <link-preview :message="message"></link-preview>
                    <p class="timestamp">{{ message.created }}</p>
                </div>
            </div>
        </div>
        <div class="flex-row flex-align-center message-form">
            <input class="flex-grow" type="text" v-model="messageForm.comment" @keyup="handleKeyPress" :placeholder="'Message '+getPlaceholder()" />
            <button class="show" @click="createMessage"><i class="fas fa-paper-plane" title="Send"></i></button>
        </div>
    </div>
</div>
`;

export default {
    name: 'Messages',
    template,
    components: {
        'link-preview': LinkPreview,
        'infinite-loading': V3InfiniteLoading.default,
    },
    setup () {
        const authStore = useAuthStore();
        const appStore = useAppStore();

        // #region rooms

        const users = ref([]);
        const rooms = ref([]);
        const currentRoom = ref({});
        const taggedRooms = ref([]);
        const menuOpen = ref(false);

        const channels = computed(() => {
            return rooms.value.filter(room => { return room.private === false; })
        });

        const directs = computed(() => {
            return rooms.value.filter(room => { return room.private === true; })
        });

        const filteredUsers = computed(() => {
            var directPeers = directs.value.map(d => d.peer)
            return users.value.filter(object1 => {
                return !directPeers.some(object2 => {
                    return object1.id === object2.id;
                });
            });
        });

        function loadRoom(room) {
            menuOpen.value = false;
            // don't load the same room over itself
            if (currentRoom.value.id !== room.id) {
                currentRoom.value = room;
                untagRoom(room);
                console.log(`Loaded room: id=${room.id}, name=${room.name}`);
            };
        };

        function createRoom(user) {
            var member_ids = [authStore.userInfo.id, user.id];
            var room = {private: true, member_ids: member_ids};
            socket.emit('create-room', room);
        };

        function isSelected(room) {
            return room.id === currentRoom.value.id;
        };

        function tagRoom(room) {
            var index = taggedRooms.value.findIndex(r => r.id === room.id);
            if (index === -1) {
                taggedRooms.value.push(room);
            };
        };

        function untagRoom(room) {
            var index = taggedRooms.value.findIndex(r => r.id === room.id);
            if (index !== -1) {
                taggedRooms.value.splice(index, 1);
            };
        };

        function isTagged(room) {
            return (taggedRooms.value.findIndex(r => r.id === room.id) !== -1) ? true : false;
        };

        function toggleMenu() {
            menuOpen.value = !menuOpen.value;
        };

        // #endregion

        // #region messages

        const messages = ref([]);
        const cursor = ref(null);
        const infiniteId = ref(null);
        const scrollContainer = ref(null);
        const messageForm = ref({
            comment: '',
        });
        // (1/4) monkey patch for bug in the infinite loading library
        let prevHeight = 0;
        // intentionally not reactive to avoid re-rendering on logout
        const currentUser = authStore.userInfo;

        watch(currentRoom, () => {
            messages.value = [];
            cursor.value = null;
            // (2/4) monkey patch for bug in the infinite loading library
            prevHeight = 0;
            infiniteId.value = currentRoom.value.id;
        });

        async function getMessages($state) {
            // (3/4) monkey patch for bug in the infinite loading library
            prevHeight = scrollContainer.value.scrollHeight;
            let query = '';
            if (cursor.value) {
                query = '?cursor=' + cursor.value;
            };
            try {
                const json = await Message.all(currentRoom.value.id, query);
                cursor.value = json.cursor;
                // prepend messages with the older messages
                messages.value.unshift(...json.messages);
                if (json.next) {
                    $state.loaded();
                } else {
                    $state.complete();
                    // (4/4) monkey patch for bug in the infinite loading library
                    nextTick(() => {
                        scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight - prevHeight;
                    });
                };
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        function infiniteHandler($state) {
            getMessages($state);
        };

        function scrollToEnd() {
            var element = scrollContainer.value;
            element.scrollTop = element.scrollHeight;
        };

        function getPlaceholder() {
            if (currentRoom.value.private === true) {
                return currentRoom.value.peer.name;
            };
            return currentRoom.value.name;
        };

        function handleKeyPress(event) {
            if (event.keyCode === 13) {
                createMessage();
            };
        };

        function createMessage() {
            if (messageForm.value.comment) {
                socket.emit('create-message', {message: messageForm.value, room: currentRoom.value});
                messageForm.value.comment = '';
            };
        };

        function deleteMessage(message) {
            socket.emit('delete-message', {message: message, room: currentRoom.value});
        };

        function isEditable(message) {
            return currentUser.id === message.author.id || currentUser.role === 'admin';
        };

        // #endregion

        // #region socket events

        socket.on('log', (data) => {
            console.log(`[Server] ${data}`);
        });

        socket.on('loadUsers', (data) => {
            users.value = data.users.filter(user => user.id != authStore.userInfo.id);
            console.log('Users preloaded.');
        });

        socket.on('loadRooms', (data) => {
            data.rooms.forEach(room => {
                if (!rooms.value.find(e => e.id === room.id)) {
                    rooms.value.push(room);
                    console.log(`Preloaded room: id=${room.id}, name=${room.name}`);
                    socket.emit('join-room', room);
                };
            });
        });

        socket.on('loadRoom', (data) => {
            loadRoom(data);
        });

        socket.on('newMessage', (message) => {
            if (message.room.id === currentRoom.value.id) {
                messages.value.push(message);
                nextTick(() => {
                    scrollToEnd();
                });
            } else {
                tagRoom(message.room);
            };
        });

        socket.on('delMessage', (message) => {
            if (message.room.id === currentRoom.value.id) {
                var index = messages.value.findIndex(m => m.id === message.id);
                if (index !== -1) {
                    messages.value.splice(index, 1);
                };
            };
        });

        // #endregion

        if (authStore.isLoggedIn) {
            // if using Bearer authentication, send the access token as a query string parameter
            // socketio doesn't support custom headers for websocket transports
            if (authStore.accessToken !== null) {
                socket.io.opts.query.access_token = authStore.accessToken;
            }
            socket.open();
        };

        onBeforeUnmount(() => {
            socket.off();
            socket.close();
            console.log('Socket disconnected.');
        });

        return {
            // rooms
            users,
            rooms,
            currentRoom,
            taggedRooms,
            menuOpen,
            channels,
            directs,
            filteredUsers,
            loadRoom,
            createRoom,
            isSelected,
            isTagged,
            toggleMenu,
            // messages
            messages,
            scrollContainer,
            infiniteId,
            messageForm,
            infiniteHandler,
            getPlaceholder,
            handleKeyPress,
            createMessage,
            deleteMessage,
            isEditable,
        };
    },
};
