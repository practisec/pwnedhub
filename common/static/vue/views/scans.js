var Scans = Vue.component("scans", {
    template: `
        <div class="flex-column scans">
            <scan-form v-on:create="createScan"></scan-form>
            <hr>
            <scans-table v-bind:scans="scans" v-on:delete="deleteScan"></scans-table>
        </div>
    `,
    data: function() {
        return {
            polling: null,
            scans: [],
        }
    },
    methods: {
        pollScans () {
            this.polling = setInterval(() => {
                this.getScans();
            }, 10000)
        },
        getScans: function() {
            fetch(store.getters.getApiUrl+"/scans", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.scans = json.scans;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        createScan: function(payload) {
            fetch(store.getters.getApiUrl+"/scans", {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(payload),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.scans.push(json)
            })
            .catch(error => store.dispatch("createToast", error));
        },
        deleteScan: function(scan) {
            fetch(store.getters.getApiUrl+"/scans/"+scan.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => {
                this.scans.splice(this.scans.findIndex(s => s.id === scan.id), 1);
            })
            .catch(error => {
                store.dispatch("createToast", error)
            });
        },
    },
    beforeDestroy () {
        clearInterval(this.polling)
    },
    created: function() {
        this.getScans();
        this.pollScans();
    },
});

Vue.component("scan-form", {
    template: `
        <div class="scan-form">
            <select v-model="scanForm.tid" v-on:change="selectTool">
                <option value="" disabled selected>Select a tool</option>
                <option v-for="tool in tools" v-bind:key="tool.id" v-bind:value="tool.id">{{ tool.name }}</option>
            </select>
            <div class="flex-column scan-form-args">
                <input type="text" v-model="scanForm.args" v-on:keyup="handleKeyPress" placeholder="Arguments here..." />
                <button class="show" v-on:click="createScan"><i class="fas fa-paper-plane" title="Send"></i></button>
            </div>
            <div class="scan-form-meta">Description: <span v-if="selectedTool">{{ selectedTool.description }}</span></div>
        </div>
    `,
    data: function() {
        return {
            tools: [],
            selectedTool: {},
            scanForm: {
                tid: "",
                args: "",
            },
        }
    },
    methods: {
        getTools: function() {
            fetch(store.getters.getApiUrl+"/tools", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.tools = json.tools;
            })
            .catch(error => store.dispatch("createToast", error));
        },
        selectTool: function() {
            this.selectedTool = this.tools.find(tool => { return tool.id == event.target.value })
        },
        handleKeyPress: function(event) {
            if (event.keyCode === 13) {
                this.createScan();
            }
        },
        createScan: function() {
            this.$emit('create', this.scanForm);
        },
    },
    created: function() {
        this.getTools();
    },
});

Vue.component("scans-table", {
    props: {
        scans: Array,
    },
    template: `
        <div v-if="scans.length > 0" class="responsive-table scans-table">
            <div class="responsive-table-headers">
                <div class="responsive-table-header" style="flex-basis: 40%;">{{ headings.command }}</div>
                <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.created }}</div>
                <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.modified }}</div>
                <div class="responsive-table-header" style="flex-basis: 10%;">{{ headings.complete }}</div>
                <div class="responsive-table-header" style="flex-basis: 10%;"></div>
            </div>
            <div class="responsive-table-body">
                <scan v-for="scan in scans" v-bind:key="scan.id" v-bind:scan="scan" v-bind:headings="headings"  v-on:delete="deleteScan"></scan>
            </div>
        </div>
    `,
    data: function() {
        return {
            headings: {
                command: "Command",
                created: "Created",
                modified: "Updated",
                complete: "Status",
            }
        }
    },
    methods: {
        deleteScan: function(scan) {
            this.$emit('delete', scan);
        },
    },
});

Vue.component("scan", {
    props: {
        scan: Object,
        headings: Object,
    },
    template: `
        <div class="responsive-table-row scans-table-row shaded-light rounded" v-on:click="getResults">
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
                <div>{{ scan.complete ? "finished" : "in progress" }}</div>
            </div>
            <div class="responsive-table-cell" style="flex-basis: 10%;">
                <div class="mobile-header">Actions</div>
                <div class="actions-cell">
                    <a class="img-btn" v-on:click.stop="deleteScan(scan)">
                        <i class="fas fa-trash" title="Delete"></i>
                    </a>
                </div>
            </div>
        </div>
    `,
    data: function() {
        return {
            results: "",
        }
    },
    methods: {
        getResults: function() {
            fetch(store.getters.getApiUrl+"/scans/"+this.scan.id+"/results", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.results = json.results;
                this.showModal();
            })
            .catch(error => store.dispatch("createToast", error));
        },
        showModal: function() {
            store.dispatch("showModal", {componentName: 'results-modal', props: {results: this.results}});
        },
        deleteScan: function(scan) {
            this.$emit('delete', scan);
        },
    },
});

var ResultsModal = Vue.component("results-modal", {
    props: {
        results: String,
    },
    template: `
        <div class="scans-modal">
            <pre>{{ results }}</pre>
        </div>
    `,
});
