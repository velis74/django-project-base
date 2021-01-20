import Vue from 'vue';
import {TitleBarData} from './titlebarData';
import {Store} from './../../store';

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
      }
    };
  },
  created() {
    this.loadData();
    this.dataStore.getProjects(this.setProjects);
  },
  mounted() {

  },
  computed: {
    currentBreadcrumbsLocation() {
      return window.location.pathname.split('/');
    },
    loggedIn() {
      return false;
      return Store.get('current-user');
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
      console.log(this.loginModel);
    },
  },
  watch: {}
});

let TitleBar = null;

if (document.getElementById('django-project-base-titlebar')) {
  TitleBar = new Vue({
    el: '#django-project-base-titlebar'
  });
}

export default {TitleBar};