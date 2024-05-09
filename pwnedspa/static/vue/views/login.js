import GoogleLogin from '../components/google-login.js';
import { useAuthStore } from '../stores/auth-store.js';

const { ref } = Vue;

const template = `
<div class="login center">
    <div class="flex-column flex-justify-center">
        <div>
            <img style="max-width: 100%;" src="/static/common/images/logo.png" />
        </div>
        <div class="center-content">
            <h3>A <span class="red">collaborative</span> space to conduct <span class="red">hosted</span> security assessments.</h3>
        </div>
    </div>
    <div class="flex-column flex-justify-center">
        <div class="flex-column form rounded">
            <label for="email">Email:</label>
            <input name="email" type="text" v-model="loginForm.email" />
            <input type="button" @click="doFormLogin" value="Log me in please." />
            <div class="gutter-bottom center-content bolded">OR</div>
            <div class="center-content">
                <google-oidc />
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

        const loginForm = ref({
            email: '',
        });

        function doFormLogin() {
            authStore.doLogin(loginForm.value);
        };

        return {
            loginForm,
            doFormLogin,
        };
    },
};
