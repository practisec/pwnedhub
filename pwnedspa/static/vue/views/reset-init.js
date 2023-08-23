import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;

const template = `
<div class="flex-column reset">
    <div class="flex-column form rounded">
        <h3>Forgot your password?</h3>
        <p>Don't worry. It happens to the best of us.</p>
        <label for="credential">Email address or username:</label>
        <input name="credential" type="text" v-model="credentialForm.credential" />
        <input type="button" @click="initializeReset" value="Please email me a recovery link." />
    </div>
</div>
`;

export default {
    name: 'ResetInit',
    template,
    setup () {
        const appStore = useAppStore();

        const credentialForm = ref({
            credential: '',
        });

        function initializeReset() {
            fetchWrapper.post(`${API_BASE_URL}/password-reset`, credentialForm.value)
            .then(json => {
                credentialForm.value.credential = '';
                appStore.createToast('Password reset email sent.');
            })
            .catch(error => appStore.createToast(error));
        };

        return {
            credentialForm,
            initializeReset,
        };
    },
};
