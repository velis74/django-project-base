import {breadcrumbs as breadcrumbsDef} from './definitions/breadcrumbs';
import {login as loginDef} from './definitions/login';
import {projectList as projectListDef} from './definitions/projectList';
import {titlebar as titlebarDef} from './definitions/titlebar';
import {userProfile as userProfileDef} from './definitions/userProfile';

import Vue from 'vue';
import {createApp} from './apps';

window.Vue = Vue;
window.createApp = createApp;
window.breadcrumbs = breadcrumbsDef;
window.login = loginDef;
window.projectList = projectListDef;
window.titlebar = titlebarDef;
window.userProfile = userProfileDef;


