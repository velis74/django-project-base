class Store {

  static store() {
    return localStorage;
  }

  static get(key) {
    let _storeData = Store.store().getItem(key);
    if (_storeData) {
      return JSON.parse(_storeData).__val;
    }
    return null;
  }

  static set(key, data) {
    if (data !== null) {
      Store.store().setItem(key, JSON.stringify({
        '__val': data
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

export {Store};