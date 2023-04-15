import { AxiosRequestConfig } from 'axios';
import { defineStore } from 'pinia';

import { apiClient, setCurrentProject } from '../../apiClient';

import {
  UserDataJSON,
  UserSessionData,
  Project,
  PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME,
  PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME,
} from './data-types';

const useUserSessionStore = defineStore('user-session', {
  state: (): UserSessionData => ({
    userData: {
      [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: 0,
      fullName: '',
      email: '',
      username: '',
      avatar: '',
    },
    impersonated: false,
    selectedProject: {
      [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: '',
      logo: '',
      name: '',
    },
  }),
  getters: {
    apiEndpointLogin() { return '/account/login'; },
    apiEndpointLogout() { return '/account/logout'; },
    apiEndpointCurrentProfile() { return '/account/profile/current'; },

    /**
     * indicates whether we are anonymous or logged in with a registered profile
     * @return: true when logged in with a registered profile, false when anonymous
     */
    loggedIn(state) { return state.userData.username !== ''; },

    /**
     * Returns a printable version of user profile, searching profile data for first printable match
     *
     * @return: any piece of data in user profile that is printable (non-empty)
     */
    userDisplayName(state) {
      const userData = state.userData;
      if (userData.fullName) return userData.fullName;
      if (userData.email) return userData.email;
      if (userData.username) return userData.username;
      return null;
    },

    /**
     * alias for getting primary key of the user
     */
    userId(state) {
      return state.userData[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME];
    },

    /**
     * alias for getting primary key of currently selected project
     */
    selectedProjectId(state) {
      return state.selectedProject[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME];
    },
  },
  actions: {
    setUserData(data: UserDataJSON | undefined) {
      const input = data || {} as UserDataJSON;
      this.$patch({
        userData: {
          [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: input[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] || 0,
          fullName: input.full_name || '',
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
          [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: input[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] || '',
          logo: input.logo || '',
          name: input.name || '',
        },
      });
      setCurrentProject(input[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] || '');
    },

    async login(username: string, password: string) {
      this.$reset();
      try {
        const result = await apiClient.post(
          this.apiEndpointLogin,
          { login: username, password },
          { hideErrorNotice: true } as AxiosRequestConfig,
        );
        await this.checkLogin(true);
        // TODO I don't think root is the way to go. Should be something like Django: next={url_to_go_to}
        // window.location.href = '/';
        return result;
      } catch (err: any) {
        console.error(err);
        return err;
      }
    },

    async logout() {
      try {
        await apiClient.post(this.apiEndpointLogout);
      } catch (error: unknown) {
        console.error(error);
      }
      this.$reset();
      // window.location.href = '/';
    },

    async checkLogin(showNotAuthorizedNotice = true) {
      try {
        const response = await apiClient.get(
          this.apiEndpointCurrentProfile,
          { hideErrorNotice: !showNotAuthorizedNotice } as AxiosRequestConfig,
        );
        if (this.userId !== response.data[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]) {
          this.$reset();
          this.setUserData(response.data);
        }
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
