// eslint-disable-next-line import/no-extraneous-dependencies
import Notifications from '@kyvg/vue3-notification';
// import ModalHandler from 'dynamicforms/src/components/modalhandler.vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import createDynamicForms from 'dynamicforms';
import { createApp } from 'vue';
import { createVuetify } from 'vuetify';

// Dokler nimamo npm packageja je najbolje, da se dynamicforms poveže preko npm link-a:
//  - Na dynamicforms narediš "npm run build", in "npm link"
//  - Na django project base narediš "npm link dynamicforms"
// Potem bi moralo delati

import Breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import Login from './components/bootstrap/login.vue';
import ProjectList from './components/bootstrap/projectlist.vue';
import TitleBar from './components/bootstrap/titlebar.vue';
import UserProfile from './components/bootstrap/userprofile.vue';
import BrowserCheck from './components/browser-check.vue';
import CookieNotice from './components/cookie-notice.vue';
import Notification from './components/notification.vue';

const componentsConfig = {
  TitleBar,
  Breadcrumbs,
  Login,
  ProjectList,
  UserProfile,
  Notification,
  BrowserCheck,
  CookieNotice,
};

const createCoreApp = (elementId: any, template, modalId, data = {}) => {
  if (typeof window.dynamicforms === 'undefined') {
    window.dynamicforms = {};
  }
  // if (!window.dynamicforms.dialog && modalId) {
  //   // eslint-disable-next-line no-new
  //   const ModalApp = createApp({ template: '<ModalHandler></ModalHandler>' });
  //   ModalApp.component(ModalHandler);
  //   ModalApp.mount(`#${modalId}`);
  // }
  const app = createApp({ data: () => data, template });
  Object.values(componentsConfig).map((component) => app.component(component.name, component));
  app.use(Notifications);
  app.use(createVuetify());
  app.use(createDynamicForms());
  app.mount(`#${elementId}`);

  return app;
};

export default createCoreApp;
