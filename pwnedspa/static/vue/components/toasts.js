import { useAppStore } from '../stores/app-store.js';

const template = `
<transition-group name="toasts" tag="div" class="flex-column toasts">
    <div class="toast" v-for="toast in appStore.toasts" :key="toast.id" :style="{ zIndex: 100-toast.id }">{{ toast.text }}</div>
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
