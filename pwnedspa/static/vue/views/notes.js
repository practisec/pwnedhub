import { useAppStore } from '../stores/app-store.js';
import { Note } from '../services/api.js';
import { marked } from '../libs/marked.js'; // esm build

const { ref, computed, onBeforeUnmount } = Vue;

const template = `
<div class="flex-column notes">
    <div class="flex-row flex-wrap tabs">
        <input id="edit" type="radio" name="grp" :checked="isActive('edit')" @click="setActive('edit')" />
        <label for="edit">Edit</label>
        <input id="view" type="radio" name="grp" :checked="isActive('view')" @click="renderNote(); setActive('view')" />
        <label for="view">View</label>
        <span class="notes-status" :class="{ 'notes-status-error': syncStatus === 'failed' }" :title="statusTitle">
            <i class="fas" :class="statusIcon"></i>
        </span>
    </div>
    <div class="flex-grow flex-row tab-content">
        <div class="flex-grow flex-row" :class="{ 'active': isActive('edit') }">
            <textarea class="flex-grow" name="notes" id="notes" v-model="note" @input="scheduleSave"></textarea>
        </div>
        <div class="flex-grow markdown" :class="{ 'active': isActive('view') }" v-html="markdown"></div>
    </div>
</div>
`;

export default {
    name: 'Notes',
    template,
    setup () {
        const appStore = useAppStore();

        const note = ref('');
        const markdown = ref('');
        const activePane = ref('view');
        const syncStatus = ref('synced');

        let saveTimer = null;

        const statusIcon = computed(() => {
            if (syncStatus.value === 'syncing') return 'fa-arrows-rotate fa-spin';
            if (syncStatus.value === 'failed') return 'fa-circle-exclamation';
            return 'fa-circle-check';
        });

        const statusTitle = computed(() => {
            if (syncStatus.value === 'syncing') return 'Syncing...';
            if (syncStatus.value === 'failed') return 'Sync failed';
            return 'Synced';
        });

        async function getNote() {
            try {
                const json = await Note.all();
                note.value = json.content;
                renderNote();
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        function renderNote() {
            if (note.value != null) {
                markdown.value = marked.parse(note.value);
            };
        };

        function scheduleSave() {
            syncStatus.value = 'syncing';
            clearTimeout(saveTimer);
            saveTimer = setTimeout(syncNotes, 1000);
        };

        async function syncNotes() {
            try {
                await Note.replace({content: note.value});
                syncStatus.value = 'synced';
            } catch (error) {
                syncStatus.value = 'failed';
                appStore.createToast(error.message);
            };
        };

        function isActive(tab) {
            return activePane.value === tab;
        };

        function setActive(tab) {
            activePane.value = tab;
        };

        onBeforeUnmount(() => {
            clearTimeout(saveTimer);
        });

        getNote();

        return {
            note,
            markdown,
            syncStatus,
            statusIcon,
            statusTitle,
            isActive,
            setActive,
            renderNote,
            scheduleSave,
        };
    },
};
