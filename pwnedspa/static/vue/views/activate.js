import { useAppStore } from '../stores/app-store.js';
import { User } from '../services/api.js';

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

        async function activateUser() {
            try {
                await User.create(activateForm.value);
                appStore.createToast('Account activated. Please log in.');
            } catch (error) {
                appStore.createToast(error.message);
            };
            router.push({ name: 'login' });
        };

        activateUser();
    },
};
