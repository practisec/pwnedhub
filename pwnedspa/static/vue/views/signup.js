import PasswordField from '../components/password-field.js';
import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;
const { useRouter }  = VueRouter;

const template = `
<div class="signup">
    <div class="flex-column about">
        <h3>Welcome to Pwned<span class="red"><b>Hub</b></span>!</h3>
        <p>The ability to consolidate and organize testing tools and results during client engagements is key for consultants dealing with short timelines and high expectations. Unfortunately, today's options for cloud resourced security testing are poorly designed and fail to support even the most basic needs. PwnedHub attempts to solve this problem by providing a space to share knowledge, execute test cases, and store the results.</p>
        <p>Developed by child prodigies Cooper ("Cooperman"), Taylor ("Babygirl#1"), and Tanner ("Hack3rPrincess"), PwnedHub was designed based on experience gained through months of security testing. The PwnedHub team is ambitions, talented, and so confident in their product, if you don't like it, they'll issue a full refund. No questions asked.</p>
        <p>So what are you waiting for? Signup today!</p>
    </div>
    <div>
        <div class="flex-column form rounded">
            <label for="username">Username: *</label>
            <input name="username" type="text" v-model="signupForm.username" />
            <label for="email">Email: *</label>
            <input name="email" type="text" v-model="signupForm.email" />
            <label for="name">Display Name: *</label>
            <input name="name" type="text" v-model="signupForm.name" />
            <label for="avatar">Avatar URL:</label>
            <input name="avatar" type="text" v-model="signupForm.avatar" />
            <label for="signature">Signature:</label>
            <textarea name="signature" v-model="signupForm.signature"></textarea>
            <label for="password">Password: *</label>
            <password-field name="password" v-model:value="signupForm.password"></password-field>
            <input type="button" @click="doSignup" value="Sign me up!" />
        </div>
    </div>
</div>
`;

export default {
    name: 'Signup',
    template,
    components: {
        'password-field': PasswordField,
    },
    setup () {
        const appStore = useAppStore();
        const router = useRouter();

        const signupForm = ref({
            username: '',
            email: '',
            name: '',
            avatar: '',
            signature: '',
            password: '',
        });

        function doSignup() {
            fetchWrapper.post(`${API_BASE_URL}/users`, signupForm.value)
            .then(json => {
                appStore.createToast('Account created. Please log in.');
                router.push({ name: 'login' });
            })
            .catch(error => appStore.createToast(error));
        };

        return {
            signupForm,
            doSignup,
        };
    },
};
