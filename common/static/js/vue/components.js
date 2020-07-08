Vue.component("password-field", {
    props: {
        name: String,
        value: String,
    },
    template: `
        <div class="flex-column" style="position: relative;">
            <input v-bind:name="name" v-bind:value="value" v-on:input="$emit('input', $event.target.value)" v-bind:type="passwordFieldType" />
            <input type="button" class="show" tabindex="-1" v-on:click="toggleShow" value="show" />
        </div>
    `,
    data: function() {
        return  {
            passwordFieldType: "password",
        }
    },
    methods: {
        toggleShow: function() {
            this.passwordFieldType = this.passwordFieldType === "password" ? "text" : "password"
        },
    },
});

Vue.component("modal", {
    template: `
        <transition name="modal">
            <div class="modal-mask flex-row flex-justify-center flex-align-center" v-on:click.self="close" v-if="visible">
                <div class="modal-container">
                    <a class="img-btn" v-on:click="close">
                        <i class="fas fa-window-close" title="Close"></i>
                    </a>
                    <component v-bind:is="component" v-bind:params="params"></component>
                </div>
            </div>
        </transition>
    `,
    computed: {
        visible: function() {
            return store.getters.modalVisible;
        },
        component: function() {
            return store.getters.modalComponent;
        },
        params: function() {
            return store.getters.modalParams;
        },
    },
    methods: {
        close: function() {
            store.dispatch("hideModal");
        },
    },
});
