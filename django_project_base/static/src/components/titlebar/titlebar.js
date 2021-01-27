import Vue from 'vue';
import Notifications from 'vue-notification';
import {TitleBarData} from './titlebarData';
import {Store} from '../../store';
import {Session} from '../../session';
import _ from 'lodash';
import {translationData} from '../../translations';
import {showNotification} from '../../notifications';

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
      permissions: {},
    };
  },
  created() {
    this.translations = translationData;
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
      let data = window.location.pathname;
      let parts = _.filter(_.trim(data, '/').split('/'), l => l);
      return _.map(parts,
        v => {
          let _idx = _.indexOf(parts, v);
          let _url = _.take(parts, _idx + 1);
          return {
            'url': '/' + _.join(_url, '/'),
            'breadcrumb': _.startCase(
              _.replace(_.replace(v, '.html', ''), ' ', ''))
          };
        }
      );
      //return brd;
      // return _.concat({
      //   'url': '/',
      //   'breadcrumb': 'Home'
      // }, brd);
    },
  },
  methods: {
    loadData() {
      this.dataStore.getData(this.setData);
      this.getPermissions();
    },
    setData(configData) {
      this.titleBarProps = configData;
    },
    setProjects(projectList) {
      this.projectList = projectList;
    },
    projectSelected(pk) {
      if (pk === Store.get('current-project').id) {
        return;
      }
      Store.set('current-project', _.first(_.filter(this.projectList, p => p.id = pk)));
      this.loadData();
    },
    makeLogin() {
      Session.login(this.loginModel.username, this.loginModel.password);
    },
    makeLogout() {
      Session.logout();
    },
    addNewProject() {
      showNotification('Make project', 'TODO');
    },
    getPermissions() {
      const permissionPromise = new Promise((resolveCallback) => {
        setTimeout(() => {
          this.permissions = {'add-project': true};
          resolveCallback();
        }, 2000);
      });
      permissionPromise.then(() => {
        console.log('pemrissions loaded');
        console.log(this.permissions);
      });
    },
  },
});

let TitleBar = null;

if (document.getElementById('django-project-base-titlebar')) {
  TitleBar = new Vue({
    el: '#django-project-base-titlebar',
  });
}

export default {TitleBar};