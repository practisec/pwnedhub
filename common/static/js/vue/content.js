Vue.component("content-wrapper", {
    template: `
        <transition-group name="toasts" tag="div" class="flex-column content-wrapper">
            <toast v-for="toast in toasts" v-bind:key="toast.id" v-bind:toast="toast"></toast>
            <div key="content" class="content">
                <div class="container-fluid">
                    <router-view></router-view>
                </div>
            </div>
        </transition-group>
    `,
    computed: {
        toasts: function() {
            return store.getters.getToasts;
        }
    },
});

Vue.component("toast", {
    props: {
        toast: Object,
    },
    template: `
        <div class="toast" v-bind:style="{ zIndex: 100-toast.id }">
            <div class="container-fluid">
                {{ toast.text }}
            </div>
        </div>
    `,
});
