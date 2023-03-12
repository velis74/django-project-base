import { AxiosRequestConfig } from 'axios';
import { defineStore } from 'pinia';

import { apiClient as ApiClient } from '../../apiClient';
import { logoutEvent } from '../../events';

import UserDataJSON = UserSession.UserDataJSON;
import UserSessionData = UserSession.UserSessionData;

const useUserSessionStore = defineStore('user-session', {
  state: (): UserSessionData => ({
    userData: {
      id: 0,
      firstName: '',
      lastName: '',
      email: '',
      username: '',
      avatar: '',
    },
    impersonated: false,
  }),
  getters: {
    loggedIn(state) { return state.userData.username !== ''; },
    userDisplayName(state) {
      const userData = state.userData;
      if (userData.firstName && userData.lastName) return `${userData.firstName} ${userData.lastName}`;
      if (userData.email) return userData.email;
      if (userData.username) return userData.username;
      return null;
    },
  },
  actions: {
    setUserData(data: UserDataJSON) {
      this.$patch({
        userData: {
          firstName: data.first_name || '',
          lastName: data.last_name || '',
          email: data.email || '',
          username: data.username || '',
        },
      });
    },

    async login(username: string, password: string) {
      this.$reset();
      try {
        await ApiClient.post('/account/login/', { login: username, password });
        await this.checkLogin(true);
        window.location.href = '/';
      } catch (err: any) {
        console.error(err);
      }
    },

    async logout() {
      try {
        await ApiClient.post('/account/logout/');
      } catch (error: unknown) {
        console.error(error);
      }
      this.$reset();
      document.dispatchEvent(logoutEvent);
      window.location.href = '/';
    },

    async checkLogin(showNotAuthorizedNotice = true) {
      try {
        const response = await ApiClient.get(
          '/account/profile/current',
          { hideErrorNotice: !showNotAuthorizedNotice } as AxiosRequestConfig,
        );
        this.$reset();
        this.setUserData(response.data);
        return true;
      } catch (error: any) {
        this.$reset();
        if (error.response && error.response.status) return error.response.status;
        throw error;
      }
    },
  },
});

export default useUserSessionStore;
