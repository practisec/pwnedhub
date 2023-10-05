import { useAuthStore } from '../stores/auth-store.js';

const { ref, onBeforeUnmount } = Vue;

const template = `
<div class="flex-column passwordless">
    <div class="flex-column form rounded">
        <h3>Check your email.</h3>
        <p>A Passwordless Authentication code has been emailed to you.</p>
        <label for="code">Code:</label>
        <input name="code" type="text" v-model="codeForm.code" />
        <input type="button" @click="doSubmitCode" value="Yes, it's really me." />
    </div>
</div>
`;

export default {
    name: 'PasswordlessAuth',
    template,
    setup () {
        const authStore = useAuthStore();

        const codeForm = ref({
            code: '',
            code_token: '',
        });

        function doSubmitCode() {
            codeForm.value.code_token = authStore.codeToken;
            authStore.doLogin(codeForm.value);
        };

        onBeforeUnmount(() => {
            authStore.unsetCodeToken();
        });

        return {
            codeForm,
            doSubmitCode,
        };
    },
};
