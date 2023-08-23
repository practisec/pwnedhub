import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';

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

        function getUser() {
            fetchWrapper.get(`${API_BASE_URL}/users/${props.userId}`)
            .then(json => {
                user.value = json;
            })
            .catch(error => appStore.createToast(error));
        };

        getUser();

        return {
            user,
        };
    },
};
