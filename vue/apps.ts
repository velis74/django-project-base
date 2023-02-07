import Notifications from '@kyvg/vue3-notification';
import createDynamicForms from 'dynamicforms';
import { createApp } from 'vue';
import { createVuetify } from 'vuetify';

import Breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import ImpersonateDialog from './components/bootstrap/impersonate-dialog.vue';
import Login from './components/bootstrap/login.vue';
import ProjectList from './components/bootstrap/projectlist.vue';
import TitleBar from './components/bootstrap/titlebar.vue';
import UserProfile from './components/bootstrap/userprofile.vue';
import BrowserCheck from './components/browser-check.vue';
import CookieNotice from './components/cookie-notice.vue';
// import Notification from './components/notification.vue';

const componentsConfig = {
  TitleBar,
  Breadcrumbs,
  Login,
  ProjectList,
  UserProfile,
  // Notification,
  BrowserCheck,
  CookieNotice,
  ImpersonateDialog,
};

const createCoreApp = (elementId: any, template: any, data = {}) => {
  const app = createApp({ data: () => data, template });
  Object.values(componentsConfig).map((component) => app.component(component.name, component));
  app.use(Notifications);
  app.use(createVuetify());
  app.use(createDynamicForms());
  app.mount(`#${elementId}`);

  return app;
};

export default createCoreApp;
