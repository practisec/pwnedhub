import { useAppStore } from '../stores/app-store.js';

const { onMounted } = Vue;

const template = `
<img id="signinBtn" class="oidc-button" src="/images/google_signin.png" />
`;

export default {
    name: 'GoogleLogin',
    template,
    setup (props, context) {
        const appStore = useAppStore();

        onMounted(() => {
            gapi.load('auth2', () => {
                const auth2 = window.gapi.auth2.init({
                    cookiepolicy: 'single_host_origin',
                });
                auth2.attachClickHandler(
                    'signinBtn',
                    {},
                    (googleUser) => {
                        context.emit('done', googleUser);
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
        });
    },
};
