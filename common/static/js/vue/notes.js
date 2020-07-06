var Notes = Vue.component("notes", {
    template: `
        <div class="flex-column notes">
            <div class="flex-row flex-wrap tabs">
                <input id="edit" type="radio" name="grp" v-bind:checked="isActive('edit')" v-on:click="setActive('edit')" />
                <label for="edit">Edit</label>
                <input id="view" type="radio" name="grp" v-bind:checked="isActive('view')" v-on:click="[setActive('view'), renderNote()]" />
                <label for="view">View</label>
            </div>
            <div class="flex-grow flex-row tab-content">
                <div class="flex-grow flex-row" v-bind:class="{ 'active': isActive('edit') }">
                    <textarea class="flex-grow" name="notes" id="notes" v-model="note" v-on:blur="updateNote"></textarea>
                </div>
                <div class="flex-grow markdown" v-bind:class="{ 'active': isActive('view') }" v-html="markdown"></div>
            </div>
        </div>
    `,
    data: function() {
        return {
            note: "",
            markdown: "",
            activePane: "view",
        }
    },
    methods: {
        getNote: function() {
            fetch(store.getters.getApiUrl+"/notes", {
                credentials: "include",
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.note = json.content;
                this.renderNote();
            })
            .catch(error => store.dispatch("createToast", error));
        },
        renderNote: function() {
            if (this.note != null) {
                this.markdown = marked(this.note);
            }
        },
        updateNote: function() {
            fetch(store.getters.getApiUrl+"/notes", {
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                method: "PUT",
                body: JSON.stringify({content: this.note}),
            })
            .then(handleErrors)
            .then(response => {})
            .catch(error => store.dispatch("createToast", error));
        },
        isActive: function(tab) {
            return this.activePane === tab;
        },
        setActive: function(tab) {
            this.activePane = tab;
        },
    },
    created: function() {
        this.getNote();
    },
});
