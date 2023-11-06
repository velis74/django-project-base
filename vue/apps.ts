import Notifications from '@kyvg/vue3-notification';
import { createDynamicForms } from '@velis/dynamicforms';
import type { Component } from '@vue/runtime-core';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createVuetify } from 'vuetify';
import { ThemeDefinition } from 'vuetify/dist/vuetify';
import 'vuetify/styles/main.css';
import '@velis/dynamicforms/styles.css';

import Breadcrumbs from './components/breadcrumbs.vue';
import BrowserCheck from './components/browser-check.vue';
import CookieNotice from './components/cookie-notice.vue';
import AppNotification from './components/notification.vue';
import NotificationsEditor from './components/notifications-editor.vue';
import ProfileSearch from './components/profile-search.vue';
import ProjectSettings from './components/project-settings.vue';
import TitleBar from './components/titlebar.vue';
import LoginDialog from './components/user-session/login-dialog.vue';
import Login from './components/user-session/login-inline.vue';
import ProjectList from './components/user-session/project-list.vue';
import UserProfile from './components/user-session/user-profile.vue';
import DefaultCookieOptions from './default-cookie-options';
import TitlebarAppStandalone from './titlebar-app-standalone.vue';

export { default as useUserSessionStore } from './components/user-session/state';
export { apiClient } from '@velis/dynamicforms';

export { default as useLoginDialog } from './components/user-session/use-login-dialog';

export { showNotification, showGeneralErrorNotification, showMaintenanceNotification } from './notifications';

export { default as showAddProfileModal } from './profile-search-add-user';

export const componentsConfig: { [key: string]: Component } = {
  TitleBar,
  Breadcrumbs,
  Login,
  ProjectList,
  UserProfile,
  AppNotification,
  BrowserCheck,
  CookieNotice,
  TitlebarAppStandalone,
  LoginDialog,
  NotificationsEditor,
  ProjectSettings,
  ProfileSearch,
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

const createCoreApp = (
  elementId: string,
  template: any,
  data: AppData = {},
  pluginsToRegister: Object = {},
  componentsToRegister: Object = {},
) => {
  const app = createApp({
    data: () => data,
    template,
  });

  // use plugins you intend to use
  app.use(createPinia());
  Object.values(pluginsToRegister).map((plugin) => app.use(plugin));

  const vuetify = createVuetify({
    defaults: { global: {} },
    theme: { defaultTheme: 'defaultTheme', themes: { defaultTheme } },
  });
  app.use(vuetify);

  app.use(createDynamicForms({ ui: 'vuetify' }));
  app.use(Notifications);

  // add translation function on a global scale
  app.provide<AppData>('data', data);

  // add components
  Object.entries(componentsConfig).map(([name, component]) => app.component(name, component));
  Object.values(componentsToRegister).map((component: Component) => app.component(component.name as string, component));

  app.mount(`#${elementId}`);

  return app;
};

export function createTitleBar(elementId: string) {
  return createCoreApp(elementId, '<titlebar-app-standalone/>');
}

export function createCookieNotice(elementId: string, cookieOptions: Object = DefaultCookieOptions) {
  return createCoreApp(elementId, '<CookieNotice/>', cookieOptions);
}

export default createCoreApp;
