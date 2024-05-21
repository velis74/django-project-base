import { apiClient } from '@velis/dynamicforms';
import { AxiosRequestConfig } from 'axios';
import { defineStore } from 'pinia';

import { setCurrentProject } from '../../api-client';

import {
  UserDataJSON,
  UserSessionData,
  Project,
  PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME,
  PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME, UserPermissionJSON,
} from './data-types';

const useUserSessionStore = defineStore('user-session', {
  state: (): UserSessionData => ({
    userData: {
      [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: 0,
      fullName: '',
      email: '',
      username: '',
      avatar: '',
      permissions: [],
      isSuperUser: false,
    },
    impersonated: false,
    passwordInvalid: false,
    deleteAt: '',
    selectedProject: {
      [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: '',
      logo: '',
      name: '',
    },
    superUserCheckStrategy: (state) => state.userData.isSuperUser,
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
     * returns (a function that tells) whether user has the named permission or not
     */
    userHasPermission: (state) => (permissionName: string): boolean => (
      state.superUserCheckStrategy(state, permissionName) ||
        !!state.userData.permissions.find((permission: UserPermissionJSON) => permission.codename === permissionName)
    ),

    /**
     * returns whether this user is a SuperUser
     */
    userIsSuperUser(state) {
      return state.userData.isSuperUser;
    },

    /**
     * alias for getting primary key of currently selected project
     */
    selectedProjectId(state) {
      return state.selectedProject?.[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME];
    },

    /**
     * alias for project name - if undefined return empty string
     */
    selectedProjectName(state) {
      return state.selectedProject?.name ?? '';
    },

    /**
     * is current user logged into any project
     */
    anyProjectSelected(state): boolean {
      return !!state.selectedProject;
    },
  },
  actions: {
    setUserData(data: UserDataJSON | undefined) {
      const permissions = (data?.permissions ?? [])
        .concat(
          (data?.groups ?? []).map((group) => (group.permissions ?? [])).flat(),
        ) ?? [];
      this.$patch({
        userData: {
          [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: data?.[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME] ?? 0,
          fullName: data?.full_name ?? '',
          email: data?.email ?? '',
          username: data?.username ?? '',
          isSuperUser: data?.is_superuser ?? false,
          permissions,
        },
        impersonated: data?.is_impersonated,
        deleteAt: data?.delete_at,
        passwordInvalid: data?.password_invalid,
      });
      if (
        !this.selectedProject?.[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME] &&
        data?.default_project?.[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]
      ) {
        this.setSelectedProject(data?.default_project);
      }
    },

    setSelectedProject(data: Project | undefined) {
      if (data === undefined) {
        this.$patch({ selectedProject: undefined });
      } else {
        this.$patch({
          selectedProject: {
            [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: data[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME],
            logo: data.logo,
            name: data.name,
          },
        });
      }
      this.checkLogin(false); // reload the profile because permissions will be different when a project is different
      setCurrentProject(data?.[PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]);
    },

    resetData(keepProject: boolean = false) {
      const sucs = this.superUserCheckStrategy;
      const project = this.selectedProject;
      this.$reset();
      if (keepProject) this.setSelectedProject(project);
      this.superUserCheckStrategy = sucs;
    },

    async login(username: string, password: string) {
      this.resetData();
      try {
        const result = await apiClient.post(
          this.apiEndpointLogin,
          { login: username, password },
          { hideErrorNotice: true } as AxiosRequestConfig,
        );
        await this.checkLogin(true);
        // TODO I don't think root is the way to go. Should be something like Django: next={url_to_go_to}
        window.location.reload();
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
      this.resetData();
      window.location.href = '/';
    },

    async checkLogin(showNotAuthorizedNotice = true) {
      try {
        const response = await apiClient.get(
          this.apiEndpointCurrentProfile,
          { hideErrorNotice: !showNotAuthorizedNotice },
        );
        if (this.userId !== response.data[PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]) this.resetData(true);
        this.setUserData(response.data);
        return true;
      } catch (error: any) {
        this.resetData();
        if (error?.response?.status) return error.response.status;
        throw error;
      }
    },
  },
});

export default useUserSessionStore;
