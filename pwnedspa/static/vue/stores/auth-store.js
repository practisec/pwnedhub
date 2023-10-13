import { useAppStore } from './app-store.js';
import { AccessToken, User } from '../services/api.js';

const { defineStore } = Pinia;
const { ref, computed } = Vue;
const { useRouter, useRoute } = VueRouter;

export const useAuthStore = defineStore('auth', () => {
    const appStore = useAppStore();
    const router = useRouter();
    const route = useRoute();

    const userInfo = ref(JSON.parse(localStorage.getItem('user')));
    const codeToken = ref(null);
    const accessToken = ref(localStorage.getItem('access_token'));
    const csrfToken = ref(localStorage.getItem('csrf_token'));

    const isLoggedIn = computed(() => {
        if (userInfo.value === null) {
            return false;
        };
        return true;
    });

    const isAdmin = computed(() => {
        if (isLoggedIn.value) {
            var user = userInfo.value;
            return (user.role === 'admin') ? true : false;
        };
        return false;
    });

    const getUserRole = computed(() => {
        if (isLoggedIn.value) {
            return userInfo.value.role;
        };
        return 'guest';
    });


    function setCodeToken(token) {
        codeToken.value = token;
    };

    function unsetCodeToken() {
        codeToken.value = null;
    };

    function setAuthTokenInfo(tokens) {
        if (tokens.csrf_token) {
            csrfToken.value = tokens.csrf_token;
            localStorage.setItem('csrf_token', tokens.csrf_token);
        };
        if (tokens.access_token) {
            accessToken.value = tokens.access_token;
            localStorage.setItem('access_token', tokens.access_token);
        };
    };

    function setAuthUserInfo(user) {
        userInfo.value = user;
        localStorage.setItem('user', JSON.stringify(user));
    };


    function unsetAuthInfo() {
        userInfo.value = null
        localStorage.removeItem('user');
        accessToken.value = null;
        localStorage.removeItem('access_token');
        csrfToken.value = null;
        localStorage.removeItem('csrf_token');
    };

    async function doLogin(payload) {
        try {
            // store auth data as necessary
            const tokens = await AccessToken.create(payload);
            setAuthTokenInfo(tokens);
            const user = await User.get('me');
            setAuthUserInfo(user);
            // route appropriately
            if (route.params.nextUrl != null) {
                // originally requested location
                router.push(route.params.nextUrl);
            } else {
                // fallback landing page
                if (user.role === 'admin') {
                    router.push({ name: 'users' });
                } else {
                    router.push({ name: 'notes' });
                };
            };
        } catch (error) {
            unsetAuthInfo();
            appStore.createToast(error.message);
        };
    };

    async function doLogout() {
        try {
            await AccessToken.delete();
            unsetAuthInfo();
            router.push({ name: 'login' });
        } catch (error) {
            appStore.createToast(error.message);
        };
    };

    return {
        userInfo,
        codeToken,
        accessToken,
        csrfToken,
        isLoggedIn,
        isAdmin,
        getUserRole,
        setCodeToken,
        unsetCodeToken,
        setAuthTokenInfo,
        setAuthUserInfo,
        unsetAuthInfo,
        doLogin,
        doLogout,
    };
});
