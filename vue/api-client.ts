import { apiClient, DfNotifications } from '@velis/dynamicforms';
import { InternalAxiosRequestConfig } from 'axios';
import { includes } from 'lodash-es';

import { HTTP_401_UNAUTHORIZED, shouldUrlBeIgnoredAfterApiResponseNotFound } from './api-config';
import { Store } from './store';

declare module 'axios' {
  export interface AxiosRequestConfig {
    hideErrorNotice: boolean;
  }
}

let currentProject = '';

export function setCurrentProject(slug: string) { currentProject = slug; }

// Add a request interceptor
// eslint-disable-next-line func-names
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig<any>) => {
    if (includes(Store.get('ignored-apis') || [], config.url)) {
      new AbortController().abort('app-canceled-err');
    }
    if (currentProject && currentProject.length) {
      config.headers['Current-Project'] = currentProject;
    }
    if (!config.headers['X-CSRFToken'] && window.csrf_token) {
      config.headers['X-CSRFToken'] = window.csrf_token;
    }
    return config;
  },
  (error: any) => Promise.reject(error),
);

// Add a response interceptor
apiClient.interceptors.response.use(
  (response: any) => Promise.resolve(response),
  (error: any) => {
    if (error.message === 'app-canceled-err') {
      return Promise.reject(error);
    }
    // eslint-disable-next-line vue/max-len
    const status = error && error.response && error.response.status ? parseInt(error.response.status, 10) : null;
    const noSession = status === HTTP_401_UNAUTHORIZED;
    const hideErrorMsg = error.config?.hideErrorNotice === true || error.config.showProgress === true;

    if (shouldUrlBeIgnoredAfterApiResponseNotFound(error)) {
      const ignoredApis = Store.get('ignored-apis') || [];
      if (!includes(ignoredApis, error.config.url)) {
        ignoredApis.push(error.config.url);
        Store.set('ignored-apis', ignoredApis);
      }
    }

    if (noSession) Store.clear();
    try {
      if (!hideErrorMsg) DfNotifications.showNotificationFromAxiosException(error);
    } catch (err: any) {
      console.log(error);
      console.error(err);
    }
    return Promise.reject(error);
  },
);

export { apiClient };
