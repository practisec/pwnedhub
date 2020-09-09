Vue.component("password-field", {
    props: {
        name: String,
        value: String,
    },
    template: `
        <div class="flex-column" style="position: relative;">
            <input v-bind:name="name" v-bind:value="value" v-on:input="$emit('input', $event.target.value)" v-bind:type="passwordFieldType" />
            <input type="button" tabindex="-1" v-on:click="toggleShow" value="show" style="background-color: transparent; position: absolute; right: 0; top: 0; border: 0;" />
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
