const { defineStore } = Pinia;
const { ref, shallowRef } = Vue;

export const useAppStore = defineStore('app', () => {
    const toasts = ref([]);
    const modalVisible = ref(false);
    const modalComponent = shallowRef(null);
    const modalProps = ref({});

    let maxToastId = 0;

    function createToast(message) {
        const id = ++maxToastId;
        toasts.value.push({id: id, text: message});
        setTimeout(() => {
            toasts.value = toasts.value.filter(t => t.id !== id)
        }, 5000);
    };

    function showModal(payload) {
        modalVisible.value = true;
        modalComponent.value = payload.componentName;
        modalProps.value = payload.props;
    };

    function hideModal() {
        modalVisible.value = false;
        modalComponent.value = null;
        modalProps.value = {};
    };

    return {
        toasts,
        modalVisible,
        modalComponent,
        modalProps,
        createToast,
        showModal,
        hideModal,
    };
});
