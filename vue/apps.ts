import Notifications from '@kyvg/vue3-notification';
import type { Component } from '@vue/runtime-core';
// import createDynamicForms from 'dynamicforms';
import { createApp } from 'vue';

import Breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import ImpersonateDialog from './components/bootstrap/impersonate-dialog.vue';
import Login from './components/bootstrap/login.vue';
import ProjectList from './components/bootstrap/projectlist.vue';
import TitleBar from './components/bootstrap/titlebar.vue';
import UserProfile from './components/bootstrap/userprofile.vue';
import BrowserCheck from './components/browser-check.vue';
import CookieNotice from './components/cookie-notice.vue';
import AppNotification from './components/notification.vue';
import DefaultCookieOptions from './defaultCookieOptions';

import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.css';
import '../django_project_base/static/fa-5.13.3/css/all.min.css';

const componentsConfig = {
  TitleBar,
  Breadcrumbs,
  Login,
  ProjectList,
  UserProfile,
  AppNotification,
  BrowserCheck,
  CookieNotice,
  ImpersonateDialog,
};

type AppData = Object;

const createCoreApp = (elementId: string, template: any, data: AppData = {}) => {
  const app = createApp({
    data: () => data,
    template,
  });
  // add components
  Object.values(componentsConfig).map((component: Component) => app.component(component.name || 'default', component));
  // use plugins you intend to use
  app.use(Notifications);
  // uncomment to add dynamic forms to project base
  // app.use(createDynamicForms());

  // add translation function on a global scale
  app.config.globalProperties.gettext = (value: string) => value;
  app.provide<AppData>('data', data);

  app.mount(`#${elementId}`);

  return app;
};

const titleBarTemplate = '<BrowserCheck :hidePageIfUnSupportedBrowser="false">' +
    '<TitleBar v-slot:content :projectlistVisible="true"/>' +
    '</BrowserCheck>';

export function createTitleBar(elementId: string) { return createCoreApp(elementId, titleBarTemplate); }

export function createCookieNotice(elementId: string, cookieOptions: Object = DefaultCookieOptions) {
  return createCoreApp(elementId, '<CookieNotice/>', cookieOptions);
}

export default createCoreApp;
