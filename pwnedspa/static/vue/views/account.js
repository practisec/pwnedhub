import PasswordField from '../components/password-field.js';
import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;

const template = `
<div class="account">
    <div class="flex-column flex-justify-end">
        <div class="flex-grow flex-row flex-align-center">
            <div class="avatar">
                <router-link :to="{ name: 'profile', params: {userId: currentUser.id} }" class="flex-grow">
                    <img class="circular bordered-dark" :src="currentUser.avatar" title="Avatar" />
                </router-link>
            </div>
        </div>
        <div class="flex-column form">
            <label for="new_password">New Password: *</label>
            <password-field name="new_password" v-model:value="passwordForm.new_password"></password-field>
            <label for="current_password">Current Password: *</label>
            <password-field name="current_password" v-model:value="passwordForm.current_password"></password-field>
            <input type="button" @click="updatePassword" value="Update my password." />
        </div>
    </div>
    <div class="flex-column flex-justify-end">
        <div class="flex-column form">
            <label for="username">Username: *</label>
            <input name="username" type="text" v-model="userForm.username" />
            <label for="email">Email: *</label>
            <input name="email" type="text" v-model="userForm.email" />
            <label for="avatar">Avatar URL:</label>
            <input name="avatar" v-model="userForm.avatar" type="text"/>
            <label for="signature">Signature:</label>
            <textarea name="signature" v-model="userForm.signature"></textarea>
            <label for="name">Display Name: *</label>
            <input name="name" v-model="userForm.name" type="text" />
            <input type="button" @click="updateUser" value="Update my account information." />
        </div>
    </div>
</div>
`;

export default {
    name: 'Account',
    template,
    components: {
        'password-field': PasswordField,
    },
    setup () {
        const authStore = useAuthStore();
        const appStore = useAppStore();

        const passwordForm = ref({
            new_password: '',
            current_password: '',
        });
        const userForm = ref({
            username: '',
            email: '',
            name: '',
            avatar: '',
            signature: '',
        });
        // intentionally not reactive to avoid re-rendering on logout
        const currentUser = authStore.userInfo;

        function updatePassword() {
            fetchWrapper.put(`${API_BASE_URL}/users/${currentUser.id}/password`, passwordForm.value)
            .then(json => {
                passwordForm.value.new_password = '';
                passwordForm.value.current_password = '';
                appStore.createToast('Password updated.');
            })
            .catch(error => appStore.createToast(error));
        };

        function setFormValues() {
            userForm.value.username = currentUser.username;
            userForm.value.email = currentUser.email;
            userForm.value.name = currentUser.name;
            userForm.value.avatar = currentUser.avatar;
            userForm.value.signature = currentUser.signature;
        };

        function updateUser() {
            fetchWrapper.patch(`${API_BASE_URL}/users/${currentUser.id}`, userForm.value)
            .then(json => {
                appStore.createToast('Account updated.');
                authStore.setAuthInfo({ user: json });
            })
            .catch(error => appStore.createToast(error));
        };

        setFormValues();

        return {
            currentUser,
            passwordForm,
            userForm,
            updatePassword,
            updateUser,
        };
    },
};
