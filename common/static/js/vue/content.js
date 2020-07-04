Vue.component("content-wrapper", {
    template: `
        <div class="flex-grow flex-column content-wrapper">
            <transition-group name="toasts" tag="div" class="flex-column toasts">
                <toast v-for="toast in toasts" v-bind:key="toast.id" v-bind:toast="toast"></toast>
            </transition-group>
            <div key="content" class="flex-grow container-fluid content">
                <router-view></router-view>
            </div>
        </div>
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
