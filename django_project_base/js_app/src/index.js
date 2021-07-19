/* eslint-disable import/no-duplicates */
import 'es6-promise/auto';
import Vue from 'vue';
import { breadcrumbs as breadcrumbsDef } from './definitions/breadcrumbs';
import { login as loginDef } from './definitions/login';
import { projectList as projectListDef } from './definitions/projectList';
import { titlebar as titlebarDef } from './definitions/titlebar';
import { userProfile as userProfileDef } from './definitions/userProfile';
import { modalWindow as modalWindowDef } from './definitions/modalWindow';
import { showNotification } from './notifications';
import { showGeneralErrorNotification } from './notifications';
import { apiClient } from './apiClient';
import { Store } from './store';
import { ProjectBaseData } from './projectBaseData';

import { createApp, registerComponent } from './apps';

if (typeof window.gettext === 'undefined') {
  window.gettext = (v) => v;
}

Vue.prototype.gettext = window.gettext;

window.Vue = Vue;
window.createApp = createApp;
window.registerComponent = registerComponent;
window.breadcrumbs = breadcrumbsDef;
window.login = loginDef;
window.projectList = projectListDef;
window.titlebar = titlebarDef;
window.userProfile = userProfileDef;
window.modalWindow = modalWindowDef;
window.showNotification = showNotification;
window.showGeneralErrorNotification = showGeneralErrorNotification;
window.apiClient = apiClient;
window.Store = Store;
window.ProjectBaseData = ProjectBaseData;
