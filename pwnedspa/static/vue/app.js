import Background from './components/background.js';
import Toasts from './components/toasts.js';
import Modal from './components/modal.js';
import Navigation from './components/navigation.js';

const template = `
<background></background>
<toasts></toasts>
<modal></modal>
<div class="flex-grow flex-column content-wrapper">
    <navigation class="header"></navigation>
    <router-view></router-view>
</div>
`;

export default {
    name: 'App',
    template,
    components: {
        'background': Background,
        'toasts': Toasts,
        'modal': Modal,
        'navigation': Navigation,
    },
};
