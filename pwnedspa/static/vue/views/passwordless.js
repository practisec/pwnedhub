import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref, onBeforeUnmount } = Vue;
const { useRouter, useRoute } = VueRouter;

const template = `
<div class="flex-column passwordless">
    <div class="flex-column form rounded">
        <h3>Check your email.</h3>
        <p>A Passwordless Authentication code has been emailed to you.</p>
        <label for="code">Code:</label>
        <input name="code" type="text" v-model="codeForm.code" />
        <input type="button" @click="submitCode" value="Yes, it's really me." />
    </div>
</div>
`;

export default {
    name: 'PasswordlessAuth',
    template,
    setup () {
        const authStore = useAuthStore();
        const appStore = useAppStore();
        const router = useRouter();
        const route = useRoute();

        const codeForm = ref({
            code: '',
            code_token: '',
        });

        function submitCode() {
            codeForm.value.code_token = authStore.codeToken;
            fetchWrapper.post(`${API_BASE_URL}/access-token`, codeForm.value)
            .then(json => handlePasswordlessSuccess(json))
            .catch(error => handlePasswordlessFailure(error));
        };

        function handlePasswordlessSuccess(json) {
            if (json.user) {
                // store auth data as necessary
                authStore.setAuthInfo(json);
                // route appropriately
                if (route.params.nextUrl != null) {
                    // originally requested location
                    router.push(route.params.nextUrl);
                } else {
                    // fallback landing page
                    if (json.user.role === 'admin') {
                        router.push({ name: 'users' });
                    } else {
                        router.push({ name: 'notes' });
                    };
                };
            } else {
                handleLoginFailure(json.message);
            };
        };

        function handlePasswordlessFailure(error) {
            authStore.unsetAuthInfo();
            appStore.createToast(error);
        };

        onBeforeUnmount(() => {
            authStore.unsetCodeToken();
        });

        return {
            codeForm,
            submitCode,
        };
    },
};
