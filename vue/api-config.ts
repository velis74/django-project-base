import { filter, size, values } from 'lodash-es';

const HTTP_404_NOT_FOUND = 404;
const HTTP_401_UNAUTHORIZED = 401;

// todo: this config should be read from server api call to get capabilities
const API_CONFIG = {
  MAINTENANCE_NOTIFICATIONS_CONFIG: {
    url: '/maintenance-notification/',
    ignoreAfterApiResponseNotFound: true,
  },
};

const shouldUrlBeIgnoredAfterApiResponseNotFound = (error: any) => size(
  filter(values(API_CONFIG), (v) => v.url === error.config.url && v.ignoreAfterApiResponseNotFound &&
      error.response.status === HTTP_404_NOT_FOUND),
) > 0;

export { API_CONFIG, shouldUrlBeIgnoredAfterApiResponseNotFound, HTTP_401_UNAUTHORIZED };
