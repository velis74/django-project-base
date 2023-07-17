/* eslint no-underscore-dangle: 0 */
/* eslint-disable import/prefer-default-export */
class Store {
  static store() {
    return localStorage;
  }

  static get(key: string) {
    const storeData = Store.store().getItem(key);
    if (storeData) {
      return JSON.parse(storeData).__val;
    }
    return null;
  }

  static set(key: string, data: any) {
    if (data !== null) {
      Store.store().setItem(key, JSON.stringify({ __val: data }));
    }
  }

  static delete(key: string) {
    Store.store().removeItem(key);
  }

  static clear() {
    Store.store().clear();
  }
}

export { Store };
