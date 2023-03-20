import { AxiosRequestConfig } from 'axios';
import { defineStore } from 'pinia';

import { apiClient as ApiClient } from '../../apiClient';

import { UserDataJSON, UserSessionData, Project, PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME } from './data-types';

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
    selectedProject: {
      [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: 0,
      logo: '',
      name: '',
    },
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
    selectedProjectId(state) {
      return state.selectedProject[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME];
    },
  },
  actions: {
    setUserData(data: UserDataJSON | undefined) {
      const input = data || {} as UserDataJSON;
      this.$patch({
        userData: {
          firstName: input.first_name || '',
          lastName: input.last_name || '',
          email: input.email || '',
          username: input.username || '',
        },
        impersonated: input.is_impersonated,
      });
    },

    setSelectedProject(data: Project | undefined) {
      const input = data || {} as Project;
      this.$patch({
        selectedProject: {
          [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: input[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] || 0,
          logo: input.logo || '',
          name: input.name || '',
        },
      });
    },

    async login(username: string, password: string) {
      this.$reset();
      try {
        await ApiClient.post('/account/login/', { login: username, password });
        await this.checkLogin(true);
        // TODO I don't think root is the way to go. Should be something like Django: next={url_to_go_to}
        // window.location.href = '/';
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
      // window.location.href = '/';
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
