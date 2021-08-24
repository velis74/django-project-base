import { Store } from './store';
import { apiClient as ApiClient } from './apiClient';
import { logoutEvent as LogoutEvent, createEvent } from './events';
// import { PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './constants';

class Session {
  static login(username, password) {
    Store.clear();
    Store.set('redirect-to-auth', false);
    ApiClient.post('/account/login/',
      { login: username, password }).then(() => {
      // ApiClient.get('/account/profile/current').then((response) => {
      //   Store.set('current-user', response.data);
      //  todo: WE DO NOT HAVE CURRENT PROJECT FOR USER IMPLEMENTED, FOR NOW WE SKIP THIS
      // eslint-disable-next-line max-len
      // Store.set('current-project', response.data['default-project'][PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]);
      // document.dispatchEvent(createEvent('login', response.data));
      /* redirect to root */
      // window.location.href = '/';
      // });
      // eslint-disable-next-line no-return-assign
      Session.checkLogin(true, () => window.location.href = '/');
    });
  }

  static logout() {
    ApiClient.post('/account/logout/').finally(() => {
      Store.clear();
      Store.set('redirect-to-auth', true);
      document.dispatchEvent(LogoutEvent);
      window.location.href = '/';
    });
  }

  static checkLogin(showNotAuthorizedNotice = true, successCallback = null) {
    return ApiClient.get('/account/profile/current', { hideErrorNotice: !showNotAuthorizedNotice }).then((response) => {
      Store.set('current-user', response.data);
      //  WE DO NOT HAVE CURRENT PROJECT FOR USER IMPLEMENTED, FOR NOW WE SKIP THIS
      // eslint-disable-next-line max-len
      // Store.set('current-project', response.data['default-project'][PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]);
      document.dispatchEvent(createEvent('login', response.data));
      if (successCallback) {
        successCallback();
      }
    }).catch(() => {
      Store.clear();
    });
  }
}

// eslint-disable-next-line import/prefer-default-export
export { Session };
