import 'es6-promise/auto';
import Vue from 'vue';

import { apiClient } from './apiClient';
import createApp from './apps';
import { showNotification, showGeneralErrorNotification } from './notifications';
import { Store } from './store';

import './assets/global.css';

if (typeof window.gettext === 'undefined') {
  window.gettext = (v) => v;
}

Vue.config.productionTip = false;
Vue.prototype.gettext = window.gettext;

window.djangoProjectBase = {
  Vue,
  createApp,
  showNotification,
  showGeneralErrorNotification,
  apiClient,
  Store,
};
