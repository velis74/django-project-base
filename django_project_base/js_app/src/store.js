/* eslint no-underscore-dangle: 0 */
/* eslint-disable import/prefer-default-export */
class Store {
  static store() {
    return localStorage;
  }

  static get(key) {
    const storeData = Store.store().getItem(key);
    if (storeData) {
      return JSON.parse(storeData).__val;
    }
    return null;
  }

  static set(key, data) {
    if (data !== null) {
      Store.store().setItem(key, JSON.stringify({
        __val: data,
      }));
    }
  }

  static delete(key) {
    Store.store().removeItem(key);
  }

  static clear() {
    Store.store().clear();
  }
}

export { Store };
