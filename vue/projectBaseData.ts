import { Store } from './store';

class ProjectBaseData {
  // THIS FILE IS REDUNDANT, IT WILL BE REMOVED WHEN PERMISSIONS API WILL BE IMPLEMENTED
  // FOR NOW IT ONLY CONTAINS FAKE GET PERMISSIONS METHOD
  // eslint-disable-next-line class-methods-use-this
  getPermissions(callback: Function) {
    const cachedPermissions = Store.get('user-permission');
    if (cachedPermissions) {
      callback(cachedPermissions);
    }
    // eslint-disable-next-line no-underscore-dangle,@typescript-eslint/naming-convention
    let _permissions = {} as any;
    const permissionPromise = new Promise((resolveCallback: Function) => {
      setTimeout(() => {
        _permissions = { 'add-project': true, 'impersonate-user': true, 'is-staff-user': true };
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
