import {Session} from '../session';
import {apiClient as ApiClient} from '../apiClient';
import {Store} from '../store';
import {ProjectBaseData} from '../projectBaseData';
import _ from 'lodash';
import {modalWindow} from './modalWindow';


const userProfile = {
  id: 'user-profile',
  type: 'x-template',
  definition: {
    template: `#user-profile`,
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
        return this.translations('Enter any user attribute');
      },
    },
    methods: {
      setAvatarImg(profileData) {
        let avatar = profileData.avatar;
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
        let cachedProfile = Store.get('current-user');
        if (cachedProfile && !force) {
          this.componentData = this.setAvatarImg(cachedProfile);
          return;
        }
        return new Promise((resolve, reject) => {
          ApiClient.get('account/profile/current').then(profileResponse => {
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
        ApiClient.post('/account/impersonate/start', {email: this.selectedUser.email}).then(() => {
          this.impersonateModalVisible = false;
          Store.set('impersonated-user', true);
          this.reloadAfterImpersonationChange();
        });
      },
      selectUser(user) {
        this.selectedUser = user;
        this.userSearchInputQueryString = user.email;
      },
      searchUsers: _.debounce(function () {
        if (!this.userSearchInputQueryString) {
          return;
        }
        let url = `/account/profile/search/${this.userSearchInputQueryString}`;
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
    modalWindow
  ],
};

export {userProfile};
