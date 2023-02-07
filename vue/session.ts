import { apiClient as ApiClient } from './apiClient';
import { createEvent, logoutEvent } from './events';
import { Store } from './store';

class Session {
  static login(username: string, password: string) {
    Store.clear();
    ApiClient.post(
      '/account/login/',
      { login: username, password },
    ).then(() => {
      // eslint-disable-next-line no-return-assign
      Session.checkLogin(true, () => window.location.href = '/');
    });
  }

  static logout() {
    ApiClient.post('/account/logout/').finally(() => {
      Store.clear();
      document.dispatchEvent(logoutEvent);
      window.location.href = '/';
    });
  }

  static checkLogin(showNotAuthorizedNotice = true, successCallback: any = null) {
    return ApiClient.get('/account/profile/current', { hideErrorNotice: !showNotAuthorizedNotice }).then(
      (response: any) => {
        Store.set('current-user', response.data);
        document.dispatchEvent(createEvent('login', response.data));
        if (successCallback) {
          successCallback();
        }
      },
    ).catch(() => {
      Store.clear();
    });
  }
}

// eslint-disable-next-line import/prefer-default-export
export { Session };
