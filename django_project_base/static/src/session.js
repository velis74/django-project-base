import {Store} from './store';
import {apiClient as ApiClient} from './apiClient';
import {loginEvent as LoginEvent, logoutEvent as LogoutEvent} from './events';
import {showGeneralErrorNotification, showNotification} from './notifications';
import {translationData} from './translations';

class Session {
  static login(username, password) {
    ApiClient.post('dpb-rest-account/login/',
      {
        login: username,
        password: password,
      }).then(() => {
      ApiClient.get('dpb-rest/profile/current?decorate=default-project').then(response => {
        Store.set('current-user', response.data);
        Store.set('current-project', response.data['default-project']);
        document.dispatchEvent(LoginEvent);
        window.location.href = 'dpb-rest/project/slug/' + response.data['default-project'].slug;
      }).catch(error => {
        console.log(error);
        showGeneralErrorNotification();
      });
    }).catch(error => {
      if (error.response && error.response.data && (error.response.data.login || error.response.data.password)) {
        showNotification(null, translationData['invalid-login-credentials']);
      }
    });
  }

  static logout() {
    ApiClient.post('dpb-rest-account/logout/')
      .then(() => {
        Store.clear();
        document.dispatchEvent(LogoutEvent);
        window.location.href = '/';
      }).catch(() => {
      showGeneralErrorNotification();
    });

  }
}

export {Session};