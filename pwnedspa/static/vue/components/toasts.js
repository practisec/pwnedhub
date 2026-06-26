import { useAppStore } from '../stores/app-store.js';

const template = `
<transition-group name="toasts" tag="div" class="toasts">
    <div class="toast" v-for="toast in appStore.toasts" :key="toast.id" @click="appStore.removeToast(toast.id)" title="Dismiss">
        <span class="toast-text">{{ toast.text }}</span>
        <i class="fas fa-xmark toast-close" aria-hidden="true"></i>
    </div>
</transition-group>
`;

export default {
    name: 'Toasts',
    template,
    setup () {
        const appStore = useAppStore();
        return {
            appStore,
        };
    },
};
