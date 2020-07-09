Vue.component("content-wrapper", {
    template: `
        <div class="flex-grow flex-column content-wrapper">
            <navigation class="header"></navigation>
            <router-view></router-view>
        </div>
    `,
});
