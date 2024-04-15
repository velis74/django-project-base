import { apiClient } from '@velis/dynamicforms';
import { InternalAxiosRequestConfig } from 'axios';
import _ from 'lodash';

import { HTTP_401_UNAUTHORIZED, shouldUrlBeIgnoredAfterApiResponseNotFound } from './api-config';
import { showGeneralErrorNotification } from './notifications';
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
    if (_.includes(Store.get('ignored-apis') || [], config.url)) {
      new AbortController().abort('app-canceled-err');
    }
    config.headers['Content-Type'] = 'application/json';
    if (currentProject && currentProject.length) {
      config.headers['Current-Project'] = currentProject;
    }
    if (!config.headers['X-CSRFToken'] && window.csrf_token) {
      config.headers['X-CSRFToken'] = window.csrf_token;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Add a response interceptor
apiClient.interceptors.response.use(
  (response) => Promise.resolve(response),
  (error) => {
    if (error.message === 'app-canceled-err') {
      return Promise.reject(error);
    }
    // eslint-disable-next-line vue/max-len
    const errMsg = error && error.response && error.response.data && error.response.data.detail ? error.response.data.detail : '';
    const status = error && error.response && error.response.status ? parseInt(error.response.status, 10) : null;
    const noSession = status === HTTP_401_UNAUTHORIZED;
    const hideErrorMsg = error.config?.hideErrorNotice === true || error.config.showProgress === true;

    if (shouldUrlBeIgnoredAfterApiResponseNotFound(error)) {
      const ignoredApis = Store.get('ignored-apis') || [];
      if (!_.includes(ignoredApis, error.config.url)) {
        ignoredApis.push(error.config.url);
        Store.set('ignored-apis', ignoredApis);
      }
    }

    if (noSession) Store.clear();
    if (!hideErrorMsg) showGeneralErrorNotification(errMsg);
    return Promise.reject(error);
  },
);

export { apiClient };
