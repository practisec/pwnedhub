import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;
const { useRouter } = VueRouter;

export default {
    name: 'Activate',
    props: {
        activateToken: String,
    },
    setup (props) {
        const appStore = useAppStore();
        const router = useRouter();

        const activateForm = ref({
            activate_token: props.activateToken,
        });

        function activateUser() {
            fetchWrapper.post(`${API_BASE_URL}/users`, activateForm.value)
            .then(json => {
                appStore.createToast('Account activated. Please log in.');
            })
            .catch(error => {
                appStore.createToast(error);
            });
            router.push({ name: 'login' });
        };

        activateUser();
    },
};
