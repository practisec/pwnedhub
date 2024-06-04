import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';

const { onMounted } = Vue;

const template = `
<img id="signinBtn" class="oidc-button" src="/static/common/images/google_signin.png" />
`;

export default {
    name: 'GoogleLogin',
    template,
    setup (props, context) {
        const authStore = useAuthStore();
        const appStore = useAppStore();

        onMounted(() => {
            if (window.hasOwnProperty("gapi")) {
                gapi.load('auth2', () => {
                    const auth2 = window.gapi.auth2.init({
                        cookiepolicy: 'single_host_origin',
                    });
                    auth2.attachClickHandler(
                        'signinBtn',
                        {},
                        (googleUser) => {
                            authStore.doLogin({id_token: googleUser.getAuthResponse().id_token});
                        },
                        (error) => {
                            if (error.error === 'network_error') {
                                appStore.createToast('OpenID Connect provider unreachable.');
                            } else if (error.error !== 'popup_closed_by_user') {
                                appStore.createToast('OpenID Connect error ({0}).'.format(error.error));
                            };
                        },
                    );
                });
            } else {
                document.getElementById("signinBtn").addEventListener("click", (e) => {
                    appStore.createToast('Google sign-in is not available. Check your internet connection and TLS configuration.');
                });
            }
        });
    },
};
