import { createApp } from 'vue';

import { createProjectBase } from './apps';
import Vuetify from './plugins/vuetify';
import TitlebarAppStandalone from './titlebar-app-standalone.vue';

import 'vuetify/styles/main.css';
import '@velis/dynamicforms/styles.css';
import './assets/global.css';

const app = createApp(TitlebarAppStandalone);
app.use(Vuetify);
app.use(createProjectBase());

app.mount('#app');
