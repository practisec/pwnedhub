import { useAppStore } from '../stores/app-store.js';

const template = `
<transition name="modal">
    <div class="modal-mask flex-row flex-justify-center flex-align-center" @click.self="appStore.hideModal" v-if="appStore.modalVisible">
        <div class="modal-container">
            <a class="img-btn" @click="appStore.hideModal">
                <i class="fas fa-window-close" title="Close"></i>
            </a>
            <component :is="appStore.modalComponent" v-bind="appStore.modalProps"></component>
        </div>
    </div>
</transition>
`;

export default {
    name: 'Modal',
    template,
    setup () {
        const appStore = useAppStore();
        return {
            appStore,
        };
    },
};
