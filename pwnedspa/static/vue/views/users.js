var Users = Vue.component("users", {
    template: `
        <div class="flex-column users">
            <users-table v-bind:users="users" v-on:update="updateUser"></users-table>
        </div>
    `,
    data: function() {
        return {
            users: [],
        }
    },
    methods: {
        getUsers: function() {
            fetch(store.getters.getApiUrl+"/users", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.users = json.users;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        updateUser: function(user, action) {
            var userForm = {};
            switch (action) {
                case 'demote':
                    userForm.role = 1;
                    break;
                case 'promote':
                    userForm.role = 0;
                    break;
                case 'disable':
                    userForm.status = 0;
                    break;
                case 'enable':
                    userForm.status = 1;
                    break;
            }
            fetch(store.getters.getApiUrl+"/admin/users/"+user.id, {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "PATCH",
                body: JSON.stringify(userForm),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.users.splice(this.users.findIndex(u => u.id === user.id), 1, json)
            })
            .catch(error => store.dispatch("createToast", error));
        },
    },
    created: function() {
        this.getUsers();
    },
});

Vue.component("users-table", {
    props: {
        users: Array,
    },
    template: `
        <div v-if="users.length > 0" class="responsive-table users-table">
            <div class="responsive-table-headers">
                <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.name }}</div>
                <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.username }}</div>
                <div class="responsive-table-header" style="flex-basis: 30%;">{{ headings.email }}</div>
                <div class="responsive-table-header" style="flex-basis: 10%;">{{ headings.role }}</div>
                <div class="responsive-table-header" style="flex-basis: 10%;">{{ headings.status }}</div>
                <div class="responsive-table-header" style="flex-basis: 10%;"></div>
            </div>
            <div class="responsive-table-body">
                <user v-for="user in users" v-bind:key="user.id" v-bind:user="user" v-bind:headings="headings" v-on:update="updateUser"></user>
            </div>
        </div>
    `,
    data: function() {
        return {
            headings: {
                name: "Display",
                username: "Username",
                email: "Email",
                role: "Role",
                status: "Status",
            }
        }
    },
    methods: {
        updateUser: function(user, action) {
            this.$emit('update', user, action);
        },
    },
});

Vue.component("user", {
    props: {
        user: Object,
        headings: Object,
    },
    template: `
        <div class="responsive-table-row users-table-row shaded-light rounded">
            <div class="responsive-table-cell" style="flex-basis: 20%;">
                <div class="mobile-header">{{ headings.name }}</div>
                <div class="flex-row flex-align-center">
                    <div class="avatar">
                        <router-link v-bind:to="{ name: 'profile', params: { userId: user.id } }">
                            <img class="circular bordered-dark" v-bind:src="user.avatar" title="Avatar" />
                        </router-link>
                    </div>
                    <div>{{ user.name }}</div>
                </div>
            </div>
            <div class="responsive-table-cell" style="flex-basis: 20%;">
                <div class="mobile-header">{{ headings.username }}</div>
                <div>{{ user.username }}</div>
            </div>
            <div class="responsive-table-cell" style="flex-basis: 30%;">
                <div class="mobile-header">{{ headings.email }}</div>
                <div>{{ user.email }}</div>
            </div>
            <div class="responsive-table-cell" style="flex-basis: 10%;">
                <div class="mobile-header">{{ headings.role }}</div>
                <div>{{ user.role }}</div>
            </div>
            <div class="responsive-table-cell" style="flex-basis: 10%;">
                <div class="mobile-header">{{ headings.status }}</div>
                <div>{{ user.status }}</div>
            </div>
            <div class="responsive-table-cell" style="flex-basis: 10%;">
                <div class="mobile-header">Actions</div>
                <div class="actions-cell">
                    <a v-if="user.role == 'admin'" class="img-btn" v-on:click.stop="updateUser(user, 'demote')">
                        <i class="fas fa-user-minus" title="Demote"></i>
                    </a>
                    <a v-if="user.role == 'user'" class="img-btn" v-on:click.stop="updateUser(user, 'promote')">
                        <i class="fas fa-user-plus" title="Promote"></i>
                    </a>
                    <a v-if="user.status == 'enabled'" class="img-btn" v-on:click.stop="updateUser(user, 'disable')">
                        <i class="fas fa-user-slash" title="Disable"></i>
                    </a>
                    <a v-if="user.status == 'disabled'" class="img-btn" v-on:click.stop="updateUser(user, 'enable')">
                        <i class="fas fa-user" title="Enable"></i>
                    </a>
                </div>
            </div>
        </div>
    `,
    methods: {
        updateUser: function(user, action) {
            this.$emit('update', user, action);
        },
    },
});
