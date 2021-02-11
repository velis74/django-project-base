import {TitleBarData} from '../apps/titlebar/titlebarData';
import {translationData} from '../translations';
import {Store} from '../store';
import {breadcrumbs,} from './breadcrumbs';
import {projectList} from './projectList';
import {login} from './login';
import {userProfile} from './userProfile';


const titlebar = {
  id: 'titlebar',
  definition: {
    mixins: [typeof titleBarMixin === 'undefined' ? {} : titleBarMixin], // jshint ignore:line
    data() {
      return {
        titleBarProps: {},
        dataStore: new TitleBarData(),
        loggedIn: null,
        translations: {},
      };
    },
    created() {
      this.translations = translationData;
      if (Store.get('current-user')) {
        this.loggedIn = true;
        this.loadData();
      }
      document.addEventListener('login', () => {
        this.loadData();
        this.loggedIn = true;
      });
      document.addEventListener('logout', () => {
        this.loggedIn = null;
        this.titleBarProps = {};
      });
      document.addEventListener('project-selected', () => {
        this.loadData();
      });
    },
    mounted() {
    },
    computed: {},
    methods: {
      loadData() {
        this.dataStore.getTitleBarData(this.setData);
      },
      setData(configData) {
        this.titleBarProps = configData;
      },
    },
  },
  childComponentsDefinition: [
    breadcrumbs, projectList, login, userProfile
  ],
};

export {titlebar};


