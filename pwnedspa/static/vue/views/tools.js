import { useAppStore } from '../stores/app-store.js';
import { Tool } from '../services/api.js';

const { ref } = Vue;

const template = `
<div class="flex-column tools">
    <div class="tool-form">
        <input type="text" v-model="toolForm.name" placeholder="Name" />
        <input type="text" v-model="toolForm.path" placeholder="Path" />
        <input type="text" class="flex-grow" v-model="toolForm.description" placeholder="Description" />
        <input type="button" @click="createTool" value="Add" />
    </div>
    <hr>
    <div v-if="tools.length > 0" class="responsive-table tools-table">
        <div class="responsive-table-headers">
            <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.name }}</div>
            <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.path }}</div>
            <div class="responsive-table-header" style="flex-basis: 50%;">{{ headings.description }}</div>
            <div class="responsive-table-header" style="flex-basis: 10%;"></div>
        </div>
        <div class="responsive-table-body">
            <div class="responsive-table-row tools-table-row shaded-light rounded" v-for="tool in tools" :key="tool.id">
                <div class="responsive-table-cell" style="flex-basis: 20%;">
                    <div class="mobile-header">{{ headings.name }}</div>
                    <div>{{ tool.name }}</div>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 20%;">
                    <div class="mobile-header">{{ headings.path }}</div>
                    <div><pre>{{ tool.path }}</pre></div>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 50%;">
                    <div class="mobile-header">{{ headings.description }}</div>
                    <div>{{ tool.description }}</div>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 10%;">
                    <div class="mobile-header">Actions</div>
                    <div class="actions-cell">
                        <a class="img-btn" @click="deleteTool(tool)">
                            <i class="fas fa-trash" title="Delete"></i>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
`;

export default {
    name: 'Tools',
    template,
    setup () {
        const appStore = useAppStore();

        const tools = ref([]);
        const toolForm = ref({
            name: '',
            path: '',
            description: '',
        });
        const headings = ref({
            name: 'Name',
            path: 'Path',
            description: 'Description',
        });

        async function getTools() {
            try {
                const json = await Tool.all();
                tools.value = json.tools;
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        async function createTool() {
            try {
                const json = await Tool.create(toolForm.value);
                tools.value.push(json);
                toolForm.value.name = '';
                toolForm.value.path = '';
                toolForm.value.description = '';
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        async function deleteTool(tool) {
            try {
                await Tool.delete(tool.id);
                tools.value.splice(tools.value.findIndex(s => s.id === tool.id), 1);
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        getTools();

        return {
            tools,
            toolForm,
            headings,
            createTool,
            deleteTool,
        };
    },
};
