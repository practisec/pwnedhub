import { useAuthStore } from '../stores/auth-store.js';

const { computed } = Vue;

const template = `
<div class="background" :class="backgroundClass"></div>
`;

export default {
    name: 'Background',
    template,
    setup () {
        const authStore = useAuthStore();
        const backgroundClass = computed(() => {
            return authStore.isLoggedIn ? 'background-auth' : 'background-unauth';
        });
        return {
            backgroundClass,
        };
    },
};
