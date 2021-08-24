import { apiClient as ApiClient } from './apiClient';
import { Store } from './store';

class ProjectBaseData {
  // eslint-disable-next-line class-methods-use-this
  getProjects(callback) {
    if (!Store.get('current-user')) {
      return null;
    }
    return ApiClient.get('/project').then((response) => {
      callback(response.data);
    }).catch((error) => {
      callback([]);
      // eslint-disable-next-line no-console
      console.error(error);
    });
  }

  // eslint-disable-next-line class-methods-use-this
  getPermissions(callback) {
    const cachedPermissions = Store.get('user-permission');
    if (cachedPermissions) {
      callback(cachedPermissions);
    }
    // eslint-disable-next-line no-underscore-dangle
    let _permissions = {};
    const permissionPromise = new Promise((resolveCallback) => {
      setTimeout(() => {
        _permissions = { 'add-project': true, 'impersonate-user': true };
        Store.set('user-permission', _permissions);
        resolveCallback();
      }, 100);
    });
    permissionPromise.then(() => {
      callback(_permissions);
    });
  }
}

export default ProjectBaseData;
