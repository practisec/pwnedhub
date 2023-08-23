const { defineStore } = Pinia;
const { ref, computed } = Vue;

export const useAuthStore = defineStore('auth', () => {
    const userInfo = ref(JSON.parse(localStorage.getItem('user')));
    const mfaToken = ref(null);
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


    function setMfaToken(token) {
        mfaToken.value = token;
    };

    function unsetMfaToken() {
        mfaToken.value = null;
    };

    function setAuthInfo(json) {
        userInfo.value = json.user;
        localStorage.setItem('user', JSON.stringify(json.user));
        if (json.csrf_token) {
            csrfToken.value = json.csrf_token;
            localStorage.setItem('csrf_token', json.csrf_token);
        };
        if (json.access_token) {
            accessToken.value = json.access_token;
            localStorage.setItem('access_token', json.access_token);
        };
    };

    function unsetAuthInfo() {
        userInfo.value = null
        localStorage.removeItem('user');
        accessToken.value = null;
        localStorage.removeItem('access_token');
        csrfToken.value = null;
        localStorage.removeItem('csrf_token');
    };

    return {
        userInfo,
        mfaToken,
        accessToken,
        csrfToken,
        isLoggedIn,
        isAdmin,
        getUserRole,
        setMfaToken,
        unsetMfaToken,
        setAuthInfo,
        unsetAuthInfo,
    };
});
