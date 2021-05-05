/* eslint-disable prefer-template */
/* eslint-disable import/prefer-default-export */
/* eslint-disable no-useless-concat */
/* eslint-disable arrow-parens */
/* eslint-disable object-shorthand */
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
        password: password,
      }).then(() => {
      ApiClient.get('account/profile/current?decorate=default-project').then(response => {
        Store.set('current-user', response.data);
        Store.set('current-project', response.data['default-project'][PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]);
        document.dispatchEvent(createEvent('login', response.data));
        showNotification(null,
          'Now redirect should be made to ' + 'project/' + response.data['default-project'][PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]);
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

export { Session };
