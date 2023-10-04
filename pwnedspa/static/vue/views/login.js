import GoogleLogin from '../components/google-login.js';
import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;
const { useRouter, useRoute } = VueRouter;

const template = `
<div class="login center">
    <div class="flex-column flex-justify-center">
        <div>
            <img style="max-width: 100%;" src="/images/logo.png" />
        </div>
        <div class="center-content">
            <h3>A <span class="red">collaborative</span> space to conduct <span class="red">hosted</span> security assessments.</h3>
        </div>
    </div>
    <div class="flex-column flex-justify-center">
        <div class="flex-column form rounded">
            <label for="username">Username:</label>
            <input name="username" type="text" v-model="loginForm.username" />
            <input type="button" @click="doFormLogin" value="Log me in please." />
            <div class="gutter-bottom center-content bolded">OR</div>
            <div class="center-content">
                <google-oidc @done="doOIDCLogin" />
            </div>
        </div>
    </div>
    <div class="flex-row flex-wrap flex-justify-space-evenly center-content panels">
        <div>
            <h5>Scan.</h5>
            <i class="fas fa-search large" title="Find"></i>
        </div>
        <div>
            <h5>Find.</h5>
            <i class="fas fa-bug large" title="Bug"></i>
        </div>
        <div>
            <h5>Win.</h5>
            <i class="fas fa-dollar-sign large" title="Bounty"></i>
        </div>
    </div>
</div>
`;

export default {
    name: 'Login',
    template,
    components: {
        'google-oidc': GoogleLogin,
    },
    setup () {
        const authStore = useAuthStore();
        const appStore = useAppStore();
        const router = useRouter();
        const route = useRoute();

        const loginForm = ref({
            username: '',
        });

        function doFormLogin() {
            doLogin(loginForm.value);
        };

        function doOIDCLogin(user) {
            var payload = {
                id_token: user.getAuthResponse().id_token
            };
            doLogin(payload);
        };

        function doLogin(payload) {
            fetchWrapper.post(`${API_BASE_URL}/access-token`, payload)
            .then(json => handleLoginSuccess(json))
            .catch(error => handleLoginFailure(error));
        };

        function handleLoginSuccess(json) {
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

        function handleLoginFailure(error) {
            authStore.unsetAuthInfo();
            appStore.createToast(error);
        };

        return {
            loginForm,
            doFormLogin,
            doOIDCLogin,
        };
    },
};
