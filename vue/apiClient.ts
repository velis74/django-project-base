import axios, { CreateAxiosDefaults } from 'axios';
import _ from 'lodash';

import { HTTP_401_UNAUTHORIZED, shouldUrlBeIgnoredAfterApiResponseNotFound } from './apiConfig';
import { showGeneralErrorNotification } from './notifications';
import { Store } from './store';

declare module 'axios' {
  export interface AxiosRequestConfig {
    hideErrorNotice: boolean;
  }
}

const apiClient = axios.create({
  xsrfCookieName: window.csrf_token_name || 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
} as CreateAxiosDefaults);

// TODO: Uporabi dynamic forms API client.

// Add a request interceptor
// eslint-disable-next-line func-names
apiClient.interceptors.request.use(
  (config) => {
    if (_.includes(Store.get('ignored-apis') || [], config.url)) {
      new AbortController().abort('app-canceled-err');
    }
    config.headers['Content-Type'] = 'application/json';
    config.headers['Current-Project'] = Store.get('current-project');
    if (!config.headers['X-CSRFToken']) {
      if (typeof dynamicforms !== 'undefined' && dynamicforms.csrf_token) {
        config.headers['X-CSRFToken'] = dynamicforms.csrf_token;
      } else if (window.csrf_token) {
        config.headers['X-CSRFToken'] = window.csrf_token;
      }
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
    const hideErrorMsg = error.config && error.config.hideErrorNotice === true;

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
