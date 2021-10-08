/* eslint-disable import/prefer-default-export */
/* eslint-disable no-undef */
/* eslint-disable max-len */
/* eslint-disable prefer-arrow-callback */
/* eslint-disable no-param-reassign */
/* eslint-disable arrow-body-style */
import axios from 'axios';

import { Store } from './store';

const apiClient = axios.create({
  xsrfCookieName: window.csrf_token_name || '__Host-csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
});

const HTTP_401_UNAUTHORIZED = 401;
// TODO: Uporabi dynamic forms API client.

// Add a request interceptor
// eslint-disable-next-line func-names
apiClient.interceptors.request.use(function (config) {
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
// eslint-disable-next-line func-names
}, function (error) {
  return Promise.reject(error);
});

// Add a response interceptor
apiClient.interceptors.response.use((response) => {
  return Promise.resolve(response);
},
(error) => {
  const errMsg = error && error.response && error.response.data && error.response.data.detail ? error.response.data.detail : '';
  const status = error && error.response && error.response.status ? parseInt(error.response.status, 10) : null;
  const noSession = status === HTTP_401_UNAUTHORIZED;
  const hideErrorMsg = error.config && error.config.hideErrorNotice === true;
  if (noSession) {
    Store.clear();
  }
  if (!hideErrorMsg) {
    showGeneralErrorNotification(errMsg);
  }
  return Promise.reject(error);
});

export { apiClient };
