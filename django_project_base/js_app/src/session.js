import { Store } from './store';
import { apiClient as ApiClient } from './apiClient';
import { logoutEvent as LogoutEvent, createEvent } from './events';
import { showNotification } from './notifications';
import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './constants';

class Session {
  static login(username, password) {
    Store.set('redirect-to-auth', false);
    ApiClient.post('account/login/',
      {
        login: username,
        password,
      }).then(() => {
      ApiClient.get('account/profile/current?decorate=default-project').then((response) => {
        Store.set('current-user', response.data);
        Store.set('current-project', response.data['default-project'][PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]);
        document.dispatchEvent(createEvent('login', response.data));
        showNotification(null,
          // eslint-disable-next-line no-useless-concat
          `${'Now redirect should be made to ' + 'project/'}${response.data['default-project'][PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]}`);
      });
    });
  }

  static logout() {
    ApiClient.post('account/logout/')
      .then(() => {
        Store.clear();
        Store.set('redirect-to-auth', true);
        document.dispatchEvent(LogoutEvent);
        window.location.href = '/';
      });
  }
}

// eslint-disable-next-line import/prefer-default-export
export { Session };
