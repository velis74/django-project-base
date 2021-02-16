import axios from 'axios';
import {Store} from './store';

const apiClient = axios.create({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
});

const HTTP_401_UNAUTHORIZED = 401;
const HTTP_401_MSG = 'Authentication credentials were not provided.';

// Add a request interceptor
apiClient.interceptors.request.use(function (config) {
  config.headers['Content-Type'] = 'application/json';
  return config;
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
    if ((status === HTTP_401_UNAUTHORIZED || errMsg === HTTP_401_MSG) && !Store.get('redirect-to-auth')) {
      Store.delete('current-user');
      Store.set('redirect-to-auth', true);
      window.location.href = '/';
    }
    return Promise.reject(error);
  });

export {apiClient};