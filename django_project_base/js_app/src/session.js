import {Store} from './store';
import {apiClient as ApiClient} from './apiClient';
import {logoutEvent as LogoutEvent, createEvent} from './events';
import {showNotification} from './notifications';

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
        Store.set('current-project', response.data['default-project'].id);
        document.dispatchEvent(createEvent('login', response.data));
        showNotification(null,
          'Now redirect should be made to ' + 'project/slug/' + response.data['default-project'].slug);
        // window.location.href = 'project/slug/' + response.data['default-project'].slug;
      });
    }).catch(error => {
      if (error.response && error.response.data && (error.response.data.login || error.response.data.password || error.response.data.detail)) {
        showNotification(null, gettext('Invalid login credentials')); // jshint ignore:line
      }
    });
  }

  static logout() {
    ApiClient.post('account/logout/')
      .then(() => {
        Store.clear();
        Store.set('redirect-to-auth', true);
        document.dispatchEvent(LogoutEvent);
        window.location.href = '/';
      }).catch(() => {
    });

  }
}

export {Session};