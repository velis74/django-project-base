import Vue from 'vue';
import Notifications from 'vue-notification';
import {TitleBarData} from './titlebarData';
import {Store} from '../../store';
import {Session} from '../../session';
import {translationData} from '../../translations';
import {Breadcrumbs, ProjectList} from "../../index";

Vue.use(Notifications);

Vue.component('titlebar', {
  mixins: [titleBarMixin], // jshint ignore:line
  data() {
    return {
      titleBarProps: {},
      dataStore: new TitleBarData(),
      projectList: [],
      loginModel: {
        username: null,
        password: null,
      },
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
      this.loginModel.password = null;
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
    makeLogin() {
      Session.login(this.loginModel.username, this.loginModel.password);
    },
    makeLogout() {
      Session.logout();
    },
  },
});

let TitleBar = null;

if (document.getElementById('django-project-base-titlebar')) {
  Vue.component('project-list', ProjectList);
  Vue.component('breadcrumbs', Breadcrumbs);

  TitleBar = new Vue({
    el: '#django-project-base-titlebar',
    components: {
      ProjectList,
      Breadcrumbs,
    },
  });
}

export default {TitleBar};