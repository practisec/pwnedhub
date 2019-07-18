var Navigation = Vue.component('navigation', {
    template: `
        <nav class="flex-grow container-fluid flex-row">
            <div class="brand">
                Pwned<span class="red"><b>Hub</b></span>
            </div>
            <ul class="flex-grow flex-row flex-justify-right">
                <li><span>menu</span>
                    <ul>
                        <li v-for="route in links" v-bind:key="route.id" v-bind:route="route">
                            <router-link v-bind:to="{ name: route.name }">{{ route.text }}</router-link>
                        </li>
                    </ul>
                </li>
            </ul>
        </nav>
        `,
    data: function() {
        return {
            links: [
                {
                    id: 0,
                    text: 'Messages',
                    name: 'messages',
                },
                {
                    id: 1,
                    text: 'Mail',
                    name: 'mail',
                },
            ]
        }
    },
});
