import 'es6-promise/auto';
import {breadcrumbs as breadcrumbsDef} from './definitions/breadcrumbs';
import {login as loginDef} from './definitions/login';
import {projectList as projectListDef} from './definitions/projectList';
import {titlebar as titlebarDef} from './definitions/titlebar';
import {userProfile as userProfileDef} from './definitions/userProfile';
import {showNotification} from './notifications';
import {showGeneralErrorNotification} from './notifications';
import {translate} from './translations';

import Vue from 'vue';
import {createApp, registerComponent} from './apps';


Vue.mixin({
  methods: {
    translations(v) {
      return translate(v);
    }
  }
});

window.Vue = Vue;
window.createApp = createApp;
window.registerComponent = registerComponent;
window.breadcrumbs = breadcrumbsDef;
window.login = loginDef;
window.projectList = projectListDef;
window.titlebar = titlebarDef;
window.userProfile = userProfileDef;
window.showNotification = showNotification;
window.showGeneralErrorNotification = showGeneralErrorNotification;
window.translate = translate;


