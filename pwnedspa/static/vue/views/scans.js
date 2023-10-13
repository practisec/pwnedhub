import ScansModal from '../modals/scans-modal.js';
import { useAppStore } from '../stores/app-store.js';
import { Tool, Scan } from '../services/api.js';

const { ref, onBeforeUnmount } = Vue;

const template = `
<div class="flex-column scans">
    <div class="scan-form">
        <select v-model="scanForm.tid" @change="selectTool($event.target.value)">
            <option value="" disabled selected>Select a tool</option>
            <option v-for="tool in tools" :key="tool.id" :value="tool.id">{{ tool.name }}</option>
        </select>
        <div class="flex-column scan-form-args">
            <input type="text" v-model="scanForm.args" @keyup="handleKeyPress" placeholder="Arguments here..." />
            <button class="show" @click="createScan"><i class="fas fa-paper-plane" title="Send"></i></button>
        </div>
        <div class="scan-form-meta">Description: <span v-if="selectedTool">{{ selectedTool.description }}</span></div>
    </div>
    <hr>
    <div v-if="scans.length > 0" class="responsive-table scans-table">
        <div class="responsive-table-headers">
            <div class="responsive-table-header" style="flex-basis: 40%;">{{ headings.command }}</div>
            <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.created }}</div>
            <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.modified }}</div>
            <div class="responsive-table-header" style="flex-basis: 10%;">{{ headings.complete }}</div>
            <div class="responsive-table-header" style="flex-basis: 10%;"></div>
        </div>
        <div class="responsive-table-body">
            <div
                class="responsive-table-row scans-table-row shaded-light rounded"
                v-for="scan in scans"
                :key="scan.id"
                :scan="scan"
                :headings="headings"
                @click="getResults(scan)"
            >
                <div class="responsive-table-cell" style="flex-basis: 40%;">
                    <div class="mobile-header">{{ headings.command }}</div>
                    <div><pre>{{ scan.command }}</pre></div>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 20%;">
                    <div class="mobile-header">{{ headings.created }}</div>
                    <div>{{ scan.created }}</div>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 20%;">
                    <div class="mobile-header">{{ headings.modified }}</div>
                    <div>{{ scan.modified }}</div>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 10%;">
                    <div class="mobile-header">{{ headings.complete }}</div>
                    <i class="fas" :class="scan.complete ? 'fa-check' : 'fa-spinner fa-spin'"></i>
                </div>
                <div class="responsive-table-cell" style="flex-basis: 10%;">
                    <div class="mobile-header">Actions</div>
                    <div class="actions-cell">
                        <a class="img-btn" @click.stop="deleteScan(scan)">
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
    name: 'Scans',
    template,
    setup () {
        const appStore = useAppStore();

        const scans = ref([]);
        const tools = ref([]);
        const selectedTool = ref({});
        const scanForm = ref({
            tid: '',
            args: '',
        });
        const headings = {
            command: 'Command',
            created: 'Created',
            modified: 'Updated',
            complete: 'Status',
        };

        let polling = null;

        async function getScans() {
            try {
                const json = await Scan.all();
                scans.value = json.scans;
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        function pollScans() {
            polling = setInterval(() => {
                getScans();
            }, 10000);
        };

        async function getTools() {
            try {
                const json = await Tool.all();
                tools.value = json.tools;
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        function selectTool(tool_id) {
            selectedTool.value = tools.value.find(tool => { return tool.id == tool_id });
        };

        function handleKeyPress(event) {
            if (event.keyCode === 13) {
                createScan();
            };
        };

        async function createScan() {
            try {
                const json = await Scan.create(scanForm.value);
                scans.value.push(json);
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        async function deleteScan(scan) {
            try {
                await Scan.delete(scan.id);
                scans.value.splice(scans.value.findIndex(s => s.id === scan.id), 1);
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        async function getResults(scan) {
            try {
                const json = await Scan.get(scan.id);
                showModal(json.results);
            } catch (error) {
                appStore.createToast(error.message);
            };
        };

        function showModal(results) {
            appStore.showModal({componentName: ScansModal, props: {results: results}});
        };

        onBeforeUnmount(() => {
            clearInterval(polling);
        });

        getScans();
        pollScans();
        getTools();

        return {
            scans,
            tools,
            selectedTool,
            scanForm,
            headings,
            selectTool,
            handleKeyPress,
            createScan,
            deleteScan,
            getResults,
        };
    },
};
