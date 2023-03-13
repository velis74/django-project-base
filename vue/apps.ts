import Notifications from '@kyvg/vue3-notification';
import type { Component } from '@vue/runtime-core';
// import { createDynamicForms, dfVuetifyConfiguration } from 'dynamicforms';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createVuetify } from 'vuetify';
import { ThemeDefinition } from 'vuetify/dist/vuetify';
import 'vuetify/styles/main.css';

import Breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import ImpersonateDialog from './components/bootstrap/impersonate-dialog.vue';
import BrowserCheck from './components/browser-check.vue';
import CookieNotice from './components/cookie-notice.vue';
import AppNotification from './components/notification.vue';
import TitleBar from './components/titlebar.vue';
import Login from './components/user-session/login.vue';
import ProjectList from './components/user-session/project-list.vue';
import UserProfile from './components/user-session/userprofile.vue';
import DefaultCookieOptions from './defaultCookieOptions';
import TitlebarAppStandalone from './titlebar-app-standalone.vue';

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
  TitlebarAppStandalone,
};

type AppData = Object;

const defaultTheme: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#f8f8f8',
    surface: '#ffffff',
    // 'primary-darken-1': '#3700B3',
    // 'secondary-darken-1': '#018786',
    primary: '#3f51b5',
    secondary: '#2196f3',
    accent: '#ffc107',
    error: '#f44336',
    warning: '#ff9800',
    info: '#8bc34a',
    success: '#00bcd4',
  },
};

const createCoreApp = (elementId: string, template: any, data: AppData = {}) => {
  const app = createApp({
    data: () => data,
    template,
  });

  // add components
  Object.values(componentsConfig).map((component: Component) => app.component(component.name as string, component));

  // use plugins you intend to use
  app.use(createPinia());

  const vuetify = createVuetify({ theme: { defaultTheme: 'defaultTheme', themes: { defaultTheme } } });
  app.use(vuetify);

  // app.use(createDynamicForms({ ui: 'vuetify' }));
  app.use(Notifications);

  // add translation function on a global scale
  app.config.globalProperties.gettext = (value: string) => value;
  app.config.unwrapInjectedRef = true;
  app.provide<AppData>('data', data);

  app.mount(`#${elementId}`);

  return app;
};

export function createTitleBar(elementId: string) { return createCoreApp(elementId, '<titlebar-app-standalone/>'); }

export function createCookieNotice(elementId: string, cookieOptions: Object = DefaultCookieOptions) {
  return createCoreApp(elementId, '<CookieNotice/>', cookieOptions);
}

export default createCoreApp;
