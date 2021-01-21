import {Store} from './store';
import {apiClient as ApiClient} from './apiClient';
import {loginEvent as LoginEvent, logoutEvent as LogoutEvent} from './events';

class Session {
  static login(username, password) {
    ApiClient.post('dpb-rest-accounts/login/',
      {
        login: username,
        password: password,
      }).then(() => {
      ApiClient.get('dpb-rest/profile/current?decorate=default-project').then(response => {
        Store.set('current-user', response.data);
        Store.set('current-project', response.data['default-project']);
        console.log('event trigegr');
        document.dispatchEvent(LoginEvent);
        window.location.href = 'dpb-rest/project/slug/' + response.data['default-project'].slug;
      }).catch(error => {
        console.error(error);
      });
    }).catch(error => {
      console.log(error);
    });
  }

  static logout() {
    ApiClient.post('dpb-rest-accounts/logout/')
      .then(() => {
        Store.clear();
        document.dispatchEvent(LogoutEvent);
        window.location.href = '/';
      }).catch(() => {
      console.log('Logout error');
    });

  }
}

export {Session};