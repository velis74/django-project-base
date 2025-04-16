import { createDynamicForms } from '@velis/dynamicforms';
import { createPinia } from 'pinia';
import { App } from 'vue';

import { accountRegisterVisible } from './components/user-session/use-login-dialog';
import * as DpbComponents from './dpb-components';
import * as VuetifyComponents from './vuetify-components';

// exports
export { default as useUserSessionStore } from './components/user-session/state';
export { apiClient } from '@velis/dynamicforms';
export { default as useLoginDialog } from './components/user-session/use-login-dialog';
export { showNotification, showGeneralErrorNotification, showMaintenanceNotification } from './notifications';
export { default as showAddProfileModal } from './profile-search-add-user';
export * from './dpb-components';
export { default as DpbApp } from './dpb-app.vue';

type ProjectBaseOptions = { accountRegisterVisible: boolean };

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function createProjectBase(options?: ProjectBaseOptions) {
  const install = (app: App) => {
    // plugins to use
    app.use(createPinia());

    app.use(createDynamicForms({ ui: 'vuetify' }));

    // add components
    Object.entries(DpbComponents).map(([name, component]) => app.component(name, component));
    Object.entries(VuetifyComponents).map(([name, component]) => app.component(name, component));

    if (options?.accountRegisterVisible !== undefined) {
      accountRegisterVisible.value = options.accountRegisterVisible;
    }
  };

  return { install };
}

export default createProjectBase;
