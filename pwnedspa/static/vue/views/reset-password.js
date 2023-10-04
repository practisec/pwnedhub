import PasswordField from '../components/password-field.js';
import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;
const { useRouter } = VueRouter;

const template = `
<div class="flex-column reset">
    <div class="flex-column form rounded">
        <h3>Reset your password!</h3>
        <p>And if you need us again, we'll be here, ready to help.</p>
        <label for="new_password">New password:</label>
        <password-field name="new_password" v-model:value="passwordForm.new_password"></password-field>
        <input type="button" @click="resetPassword" value="Please reset my password." />
    </div>
</div>
`;

export default {
    name: 'ResetPassword',
    template,
    props: {
        userId: [Number, String],
        resetToken: String,
    },
    components: {
        'password-field': PasswordField,
    },
    setup (props) {
        const appStore = useAppStore();
        const router = useRouter();

        const passwordForm = ref({
            new_password: '',
            reset_token: props.resetToken,
        });

        function resetPassword() {
            fetchWrapper.put(`${API_BASE_URL}/users/${props.userId}/password`, passwordForm.value)
            .then(json => {
                appStore.createToast('Password successfully reset.');
                router.push({ name: 'login' });
            })
            .catch(error => appStore.createToast(error));
        };

        return {
            passwordForm,
            resetPassword,
        };
    },
};
