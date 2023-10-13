import { useAuthStore } from '../stores/auth-store.js';
import { useAppStore } from '../stores/app-store.js';
import { User } from '../services/api.js';

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

        async function updateUser() {
            try {
                const json = await User.update(currentUser.id, userForm.value);
                authStore.setAuthUserInfo(json);
                appStore.createToast('Account updated.');
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        setFormValues();

        return {
            currentUser,
            userForm,
            updateUser,
        };
    },
};
