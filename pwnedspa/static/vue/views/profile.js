import { useAppStore } from '../stores/app-store.js';
import { User } from '../services/api.js';

const { ref } = Vue;

const template = `
<div v-if="user" class="flex-column profile center-content">
    <div class="avatar"><img class="circular bordered-dark" :src="user.avatar" title="Avatar" /></div>
    <div><h3>{{ user.name }}</h3></div>
    <div><h6>Member since: {{ user.created }}</h6></div>
    <div><blockquote>{{ user.signature }}</blockquote></div>
</div>
`;

export default {
    name: 'Profile',
    template,
    props: {
        userId: [Number, String],
    },
    setup (props) {
        const appStore = useAppStore();

        const user = ref(null);

        async function getUser() {
            try {
                const json = await User.get(props.userId);
                user.value = json;
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        getUser();

        return {
            user,
        };
    },
};
