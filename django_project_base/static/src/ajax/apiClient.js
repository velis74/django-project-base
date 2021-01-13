import axios from 'axios';


const apiClient = axios.create({
  // xsrfCookieName: 'csrftoken',
  // xsrfHeaderName: 'X-CSRFToken',
  // baseURL: '/rest/',
  baseURL: 'http://192.168.237.100:9000/',
  //withCredentials: true,
  crossDomain: true,
});

const HTTP_401_UNAUTHORIZED = 401;

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
    const status = error && error.response && error.response.status ? parseInt(error.response.status, 10) : null;
    if (status === HTTP_401_UNAUTHORIZED) {
      window.location.href = '/';
    }
    return Promise.reject(error);
  });

export {apiClient};