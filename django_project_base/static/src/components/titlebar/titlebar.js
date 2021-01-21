import Vue from 'vue';
import {TitleBarData} from './titlebarData';
import {Store} from '../../store';
import {Session} from '../../session';

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
    };
  },
  created() {
    if (Store.get('current-user')) {
      this.loggedIn = true;
      this.loadData();
      this.dataStore.getProjects(this.setProjects);
    }
    document.addEventListener('login', () => {
      this.loadData();
      this.dataStore.getProjects(this.setProjects);
      this.loggedIn = true;
    });
    document.addEventListener('logout', () => {
      this.loggedIn = null;
      this.titleBarProps = {};
      this.projectList = [];
      this.loginModel.password = null;
    });
  },
  mounted() {

  },
  computed: {
    currentBreadcrumbsLocation() {
      return window.location.pathname.split('/');
    },
  },
  methods: {
    loadData() {
      this.dataStore.getData(this.setData);
    },
    setData(configData) {
      this.titleBarProps = configData;
    },
    setProjects(projectList) {
      this.projectList = projectList;
    },
    projectSelected(pk) {
      if (pk === Store.get('current-project')) {
        return;
      }
      Store.set('current-project', pk);
      this.loadData();
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
  TitleBar = new Vue({
    el: '#django-project-base-titlebar'
  });
}

export default {TitleBar};