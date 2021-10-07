import 'es6-promise/auto';
import Vue from 'vue';

import { apiClient } from './apiClient';
import createApp from './apps';
import { showNotification, showGeneralErrorNotification } from './notifications';
import ProjectBaseData from './projectBaseData';
import { Store } from './store';

import './assets/global.css';

if (typeof window.gettext === 'undefined') {
  window.gettext = (v) => v;
}

Vue.config.productionTip = false;
Vue.prototype.gettext = window.gettext;

window.Vue = Vue;
window.createApp = createApp;
window.showNotification = showNotification;
window.showGeneralErrorNotification = showGeneralErrorNotification;
window.apiClient = apiClient;
window.Store = Store;
window.ProjectBaseData = ProjectBaseData;
