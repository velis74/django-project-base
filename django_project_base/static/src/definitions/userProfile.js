import {translationData} from '../translations';
import {Session} from '../session';
import {TitleBarData} from '../apps/titlebar/titlebarData';

const userProfileComponentDefinition = {
  defaultId: 'user-profile',
  definition: {
    mixins: [userProfileMixin], // jshint ignore:line
    data() {
      return {
        translations: {},
        componentData: {},
        dataStore: new TitleBarData(),
      };
    },
    created() {
      this.translations = translationData;
      this.loadData();
    },
    mounted() {

    },
    computed: {},
    methods: {
      loadData() {
        this.dataStore.getUserProfileData(this.setData);
      },
      setData(configData) {
        this.componentData = configData;
      },
      makeLogout() {
        Session.logout();
      }
    },
  }
};

export {userProfileComponentDefinition};
