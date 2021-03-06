import {apiClient as ApiClient} from './apiClient';
import {Store} from './store';

class ProjectBaseData {

  getProjects(callback) {
    if (!Store.get('current-user')) {
      return;
    }
    ApiClient.get('project').then(response => {
      callback(response.data);
    }).catch(error => {
      callback([]);
      console.error(error);
    });
  }

  getPermissions(callback) {
    let cachedPermissions = Store.get('user-permission');
    if (cachedPermissions) {
      callback(cachedPermissions);
    }
    let _permissions = {};
    const permissionPromise = new Promise((resolveCallback) => {
      setTimeout(() => {
        _permissions = {'add-project': true, 'impersonate-user': true};
        Store.set('user-permission', _permissions);
        resolveCallback();
      }, 2000);
    });
    permissionPromise.then(() => {
      callback(_permissions);
    });
  }

}

export {ProjectBaseData};