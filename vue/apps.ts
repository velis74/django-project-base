import Notifications from '@kyvg/vue3-notification';
import { createDynamicForms } from '@velis/dynamicforms';
import type { Component } from '@vue/runtime-core';
import { createPinia } from 'pinia';
import { App } from 'vue';
import 'vuetify/styles/main.css';
import '@velis/dynamicforms/styles.css';

import * as DpbComponents from './dpb-components';
import * as VuetifyComponents from './vuetify-components';

// exports
export { default as useUserSessionStore } from './components/user-session/state';
export { apiClient } from '@velis/dynamicforms';
export { default as useLoginDialog } from './components/user-session/use-login-dialog';
export { showNotification, showGeneralErrorNotification, showMaintenanceNotification } from './notifications';
export { default as showAddProfileModal } from './profile-search-add-user';
export * from './dpb-components';

type ProjectBaseOptions = {};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function createProjectBase(options?: ProjectBaseOptions) {
  const install = (app: App) => {
    // plugins to use
    app.use(createPinia());

    app.use(createDynamicForms({ ui: 'vuetify' }));

    app.use(Notifications);

    // add components
    Object.entries(DpbComponents).map(([name, component]) => app.component(name, component));
    Object.entries(VuetifyComponents).map(([name, component]) => app.component(name, component));
  };

  return { install };
}

export default createProjectBase;
