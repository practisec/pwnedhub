import App from './app.js';
import { router } from './router.js';

const { createApp } = Vue;
const { createPinia } = Pinia;
const pinia = createPinia();
const app = createApp(App);

app.use(router);
app.use(pinia);
app.mount('#app');
