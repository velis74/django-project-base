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
      },
      loggedIn: null,
    };
  },
  created() {
    if (Store.get('current-user')) {
      this.loadData();
      this.dataStore.getProjects(this.setProjects);
    }
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
      this.loggedIn = 3;
      Store.set('current-user', 3);
    },
  },
  watch: {
    loggedIn(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.loadData();
      }
    },
  }
});

let TitleBar = null;

if (document.getElementById('django-project-base-titlebar')) {
  TitleBar = new Vue({
    el: '#django-project-base-titlebar'
  });
}

export default {TitleBar};