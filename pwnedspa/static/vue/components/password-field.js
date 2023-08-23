const { ref } = Vue;

const template = `
<div class="flex-column" style="position: relative;">
    <input :name="name" :value="value" @input="$emit('update:value', $event.target.value)" :type="showPassword ? 'text' : 'password'" />
    <input type="button" tabindex="-1" @click="showPassword = !showPassword" value="show" style="background-color: transparent; position: absolute; right: 0; top: 0; border: 0;" />
</div>
`;

export default  {
    name: 'PasswordField',
    template,
    props: {
        name: String,
        value: String,
    },
    setup () {
        const showPassword = ref(false);
        return {
            showPassword,
        };
    },
};
