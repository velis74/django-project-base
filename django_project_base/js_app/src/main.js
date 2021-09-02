import 'es6-promise/auto';
import Vue from 'vue';

import { showNotification, showGeneralErrorNotification } from './notifications';

import { apiClient } from './apiClient';
import { Store } from './store';
import ProjectBaseData from './projectBaseData';

import './assets/global.css';

import createApp from './apps';

if (typeof window.gettext === 'undefined') {
  window.gettext = (v) => v;
}

Vue.prototype.gettext = window.gettext;

window.Vue = Vue;
window.createApp = createApp;
window.showNotification = showNotification;
window.showGeneralErrorNotification = showGeneralErrorNotification;
window.apiClient = apiClient;
window.Store = Store;
window.ProjectBaseData = ProjectBaseData;
