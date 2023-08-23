import { useAppStore } from '../stores/app-store.js';
import { fetchWrapper } from '../helpers/fetch-wrapper.js';
import { marked } from '../libs/marked.js'; // esm build

const { ref } = Vue;

const template = `
<div class="flex-column notes">
    <div class="flex-row flex-wrap tabs">
        <input id="edit" type="radio" name="grp" :checked="isActive('edit')" @click="setActive('edit')" />
        <label for="edit">Edit</label>
        <input id="view" type="radio" name="grp" :checked="isActive('view')" @click="renderNote(); setActive('view')" />
        <label for="view">View</label>
    </div>
    <div class="flex-grow flex-row tab-content">
        <div class="flex-grow flex-row" :class="{ 'active': isActive('edit') }">
            <textarea class="flex-grow" name="notes" id="notes" v-model="note" @blur="updateNote"></textarea>
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

        function getNote() {
            fetchWrapper.get(`${API_BASE_URL}/notes`)
            .then(json => {
                note.value = json.content;
                renderNote();
            })
            .catch(error => appStore.createToast(error));
        };

        function renderNote() {
            if (note.value != null) {
                markdown.value = marked.parse(note.value);
            };
        };

        function updateNote() {
            fetchWrapper.put(`${API_BASE_URL}/notes`, {content: note.value})
            .then(json => {})
            .catch(error => appStore.createToast(error));
        };

        function isActive(tab) {
            return activePane.value === tab;
        };

        function setActive(tab) {
            activePane.value = tab;
        };

        getNote();

        return {
            note,
            markdown,
            isActive,
            setActive,
            renderNote,
            updateNote,
        };
    },
};
