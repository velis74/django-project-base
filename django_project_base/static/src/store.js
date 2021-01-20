class Store {
  static get(key) {
    let _storeData = localStorage.getItem(key);
    if (_storeData) {
      return JSON.parse(_storeData).__val;
    }
    return null;
  }

  static set(key, data) {
    if (data !== null) {
      localStorage.setItem(key, JSON.stringify({
        '__val': data
      }));
    }
  }
}

export {Store};