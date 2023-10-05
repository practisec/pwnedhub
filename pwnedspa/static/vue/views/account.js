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
    </div>
    <div class="flex-column flex-justify-end">
        <div class="flex-column form">
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
    setup () {
        const authStore = useAuthStore();
        const appStore = useAppStore();

        const userForm = ref({
            email: '',
            name: '',
            avatar: '',
            signature: '',
        });
        // intentionally not reactive to avoid re-rendering on logout
        const currentUser = authStore.userInfo;

        function setFormValues() {
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
            userForm,
            updateUser,
        };
    },
};
