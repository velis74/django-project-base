import {Session} from '../session';
import {apiClient as ApiClient} from '../apiClient';
import {showGeneralErrorNotification} from '../notifications';
import {Store} from '../store';
import {ProjectBaseData} from '../projectBaseData';
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
      };
    },
    created() {
      this.loadData();
    },
    mounted() {

    },
    computed: {
    },
    methods: {
      setAvatarImg(profileData) {
        let avatar = profileData.avatar;
        if (!avatar) {
          profileData.avatar = 'https://via.placeholder.com/45';
        }
        return profileData;
      },
      loadData() {
        new ProjectBaseData().getPermissions(p => {
          this.permissions = p;
        });
        let cachedProfile = Store.get('current-user');
        if (cachedProfile) {
          this.componentData = this.setAvatarImg(cachedProfile);
          return;
        }
        ApiClient.get('account/profile/current').then(profileResponse => {
          this.componentData = this.setAvatarImg(profileResponse.data);
          Store.set('current-user', this.componentData);
        }).catch(() => {
          showGeneralErrorNotification();
        });
      },
      makeLogout() {
        Session.logout();
      },
      showImpersonateLogin() {
        console.log('modal');
      },
    },
  },
  childComponentsDefinition: [
    modalWindow,
  ],
};

export {userProfile};
