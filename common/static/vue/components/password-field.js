Vue.component("password-field", {
    props: {
        name: String,
        value: String,
    },
    template: `
        <div class="flex-column" style="position: relative;">
            <input v-bind:name="name" v-bind:value="value" v-on:input="$emit('input', $event.target.value)" v-bind:type="passwordFieldType" />
            <input type="button" class="show" tabindex="-1" v-on:click="toggleShow" value="show" />
        </div>
    `,
    data: function() {
        return  {
            passwordFieldType: "password",
        }
    },
    methods: {
        toggleShow: function() {
            this.passwordFieldType = this.passwordFieldType === "password" ? "text" : "password"
        },
    },
});
