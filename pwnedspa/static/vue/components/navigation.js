import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref, watch } = Vue;
const { useRouter, useRoute } = VueRouter;

const template = `
<div class="nav">
    <ul class="menu" :class="{ active: isOpen }">
        <li class="brand"><img src="/images/logo.png" /></li>
        <li class="toggle"><a href="#" @click.prevent="toggleMenu"><i class="fas fa-bars"></i></a></li>
        <li class="item avatar" v-if="authStore.isLoggedIn">
            <router-link :to="{ name: 'account' }">
                <img class="circular bordered-dark" :src="authStore.userInfo.avatar" title="Avatar" />
            </router-link>
        </li>
        <li class="item" v-for="route in permissions[authStore.getUserRole]" :key="route.id" :route="route">
            <router-link :to="{ name: route.name, params: route.params || {} }">{{ route.text }}</router-link>
        </li>
        <li class="item" v-if="authStore.isLoggedIn"><span @click="doLogout">Logout</span></li>
    </ul>
</div>
`;

export default {
    name: 'Navigation',
    template,
    setup () {
        const authStore = useAuthStore();
        const appStore = useAppStore();
        const router = useRouter();
        const route = useRoute();

        const isOpen = ref(false);
        const permissions = {
            guest: [
                {
                    id: 0,
                    text: 'Login',
                    name: 'login',
                },
                {
                    id: 1,
                    text: 'Signup',
                    name: 'signup',
                },
            ],
            admin: [
                {
                    id: 0,
                    text: 'Users',
                    name: 'users',
                },
                {
                    id: 1,
                    text: 'Tools',
                    name: 'tools',
                },
                {
                    id: 2,
                    text: 'Messaging',
                    name: 'messaging',
                },
            ],
            user: [
                {
                    id: 0,
                    text: 'Notes',
                    name: 'notes',
                },
                {
                    id: 1,
                    text: 'Scans',
                    name: 'scans',
                },
                {
                    id: 2,
                    text: 'Messaging',
                    name: 'messaging',
                },
            ],
        };

        watch(() => route.name, () => {
            isOpen.value = false;
        });

        function doLogout() {
            fetchWrapper.delete(`${API_BASE_URL}/access-token`)
            .then(json => {
                authStore.unsetAuthInfo();
                router.push({ name: 'login' });
            })
            .catch(error => appStore.createToast(error));
        };

        function toggleMenu() {
            isOpen.value = !isOpen.value;
        };

        return {
            authStore,
            isOpen,
            permissions,
            doLogout,
            toggleMenu,
        };
    },
};
