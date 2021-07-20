/* eslint-disable import/prefer-default-export */
/* eslint-disable arrow-parens */
/* eslint-disable prefer-destructuring */
/* eslint-disable no-param-reassign */
/* eslint-disable consistent-return */
import _ from 'lodash';
import { Session } from '../session';
import { apiClient as ApiClient } from '../apiClient';
import { Store } from '../store';
import { ProjectBaseData } from '../projectBaseData';
import { modalWindow } from './modalWindow';

const userProfile = {
  id: 'user-profile',
  type: 'x-template',
  definition: {
    template: '#user-profile',
    data() {
      return {
        componentData: {},
        permissions: {},
        impersonateModalVisible: false,
        usersFilter: [],
        selectedUser: null,
        userSearchInputQueryString: '',
        isImpersonated: false,
      };
    },
    created() {
      this.loadData();
    },
    mounted() {

    },
    computed: {
      searchUserPlaceholder() {
        return this.gettext('Enter any user attribute');
      },
    },
    methods: {
      setAvatarImg(profileData) {
        const avatar = profileData.avatar;
        if (!avatar) {
          profileData.avatar = 'https://via.placeholder.com/45';
        }
        return profileData;
      },
      loadData(force = false) {
        new ProjectBaseData().getPermissions(p => {
          this.permissions = p;
        });
        this.isImpersonated = !!Store.get('impersonated-user');
        const cachedProfile = Store.get('current-user');
        if (cachedProfile && !force) {
          this.componentData = this.setAvatarImg(cachedProfile);
          return;
        }
        return new Promise((resolve, reject) => {
          ApiClient.get('/account/profile/current').then(profileResponse => {
            this.componentData = this.setAvatarImg(profileResponse.data);
            Store.set('current-user', this.componentData);
            resolve();
          }).catch(err => {
            reject(err);
          });
        });
      },
      makeLogout() {
        Session.logout();
      },
      showImpersonateLogin() {
        this.userSearchInputQueryString = '';
        this.impersonateModalVisible = !this.impersonateModalVisible;
      },
      changeUser() {
        ApiClient.post('/account/impersonate/start', { id: this.selectedUser.id }).then(() => {
          this.impersonateModalVisible = false;
          Store.set('impersonated-user', true);
          this.reloadAfterImpersonationChange();
        });
      },
      selectUser(user) {
        this.selectedUser = user;
        this.userSearchInputQueryString = user.full_name || user.email;
      },
      searchUsers: _.debounce(function () {
        if (!this.userSearchInputQueryString) {
          return;
        }
        const url = `/account/profile?search=${this.userSearchInputQueryString}`;
        ApiClient.get(url).then((response) => {
          this.usersFilter = response.data;
        });
      }, 250),
      reloadAfterImpersonationChange() {
        this.loadData(true).then(() => {
          window.location.href = '/';
        });
      },
      stopImpersonation() {
        ApiClient.post('/account/impersonate/end').then(() => {
          Store.delete('impersonated-user');
          this.reloadAfterImpersonationChange();
        });
      },
    },
  },
  childComponentsDefinition: [
    modalWindow,
  ],
};

export { userProfile };
