Vue.component("toasts", {
    template: `
        <transition-group name="toasts" tag="div" class="flex-column toasts">
            <toast v-for="toast in toasts" v-bind:key="toast.id" v-bind:toast="toast"></toast>
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
        <div class="toast" v-bind:style="{ zIndex: 100-toast.id }">{{ toast.text }}</div>
    `,
});
