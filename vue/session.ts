import type { AxiosRequestConfig } from 'axios';

import { apiClient as ApiClient } from './apiClient';
import { createEvent, logoutEvent } from './events';
import { Store } from './store';

export default abstract class Session {
  static async login(username: string, password: string) {
    Store.clear();
    try {
      await ApiClient.post('/account/login/', { login: username, password });
      await Session.checkLogin(true);
      window.location.href = '/';
    } catch (err: any) {
      console.error(err);
    }
  }

  static async logout() {
    try {
      await ApiClient.post('/account/logout/');
    } catch (error: unknown) {
      console.error(error);
    }
    Store.clear();
    document.dispatchEvent(logoutEvent);
    window.location.href = '/';
  }

  static async checkLogin(showNotAuthorizedNotice = true) {
    try {
      const response = await ApiClient.get(
        '/account/profile/current',
        { hideErrorNotice: !showNotAuthorizedNotice } as AxiosRequestConfig,
      );
      Store.set('current-user', response.data);
      document.dispatchEvent(createEvent('login', response.data));
      return true;
    } catch (error: any) {
      Store.clear();
      if (error.response && error.response.status) return error.response.status;
      throw error;
    }
  }
}
