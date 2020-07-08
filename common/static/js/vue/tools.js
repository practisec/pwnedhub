var Tools = Vue.component("tools", {
    template: `
        <div class="flex-column tools">
            <tool-form v-on:create="createTool"></tool-form>
            <hr>
            <tools-table v-bind:tools="tools" v-on:delete="deleteTool"></tools-table>
        </div>
    `,
    data: function() {
        return {
            tools: [],
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
        createTool: function(payload) {
            fetch(store.getters.getApiUrl+"/tools", {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "POST",
                body: JSON.stringify(payload),
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.tools.push(json)
            })
            .catch(error => store.dispatch("createToast", error));
        },
        deleteTool: function(tool) {
            fetch(store.getters.getApiUrl+"/tools/"+tool.id, {
                credentials: "include",
                method: "DELETE",
            })
            .then(handleErrors)
            .then(response => {
                this.tools.splice(this.tools.findIndex(s => s.id === tool.id), 1);
            })
            .catch(error => {
                store.dispatch("createToast", error)
            });
        },
    },
    created: function() {
        this.getTools();
    },
});

Vue.component("tool-form", {
    template: `
        <div class="tool-form">
            <input type="text" v-model="toolForm.name" placeholder="Name" />
            <input type="text" v-model="toolForm.path" placeholder="Path" />
            <input type="text" class="flex-grow" v-model="toolForm.description" placeholder="Description" />
            <input type="button" v-on:click="createTool" value="Add" />
        </div>
    `,
    data: function() {
        return {
            toolForm: {
                name: "",
                path: "",
                description: "",
            },
        }
    },
    methods: {
        createTool: function() {
            if (this.toolForm.name && this.toolForm.path && this.toolForm.description) {
                this.$emit('create', this.toolForm);
                this.toolForm.name = "";
                this.toolForm.path = "";
                this.toolForm.description = "";
            }
        },
    },
});

Vue.component("tools-table", {
    props: {
        tools: Array,
    },
    template: `
        <div v-if="tools.length > 0" class="responsive-table tools-table">
            <div class="responsive-table-headers">
                <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.name }}</div>
                <div class="responsive-table-header" style="flex-basis: 20%;">{{ headings.path }}</div>
                <div class="responsive-table-header" style="flex-basis: 50%;">{{ headings.description }}</div>
                <div class="responsive-table-header" style="flex-basis: 10%;"></div>
            </div>
            <div class="responsive-table-body">
                <tool v-for="tool in tools" v-bind:key="tool.id" v-bind:tool="tool" v-bind:headings="headings"  v-on:delete="deleteTool"></tool>
            </div>
        </div>
    `,
    data: function() {
        return {
            headings: {
                name: "Name",
                path: "Path",
                description: "Description",
            }
        }
    },
    methods: {
        deleteTool: function(tool) {
            this.$emit('delete', tool);
        },
    },
});

Vue.component("tool", {
    props: {
        tool: Object,
        headings: Object,
    },
    template: `
        <div class="responsive-table-row shaded-light rounded">
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
                <div>
                    <a class="img-btn" v-on:click.stop="deleteTool(tool)">
                        <i class="fas fa-trash" title="Delete"></i>
                    </a>
                </div>
            </div>
        </div>
    `,
    methods: {
        deleteTool: function(tool) {
            this.$emit('delete', tool);
        },
    },
});
