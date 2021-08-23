/* eslint-disable no-unused-vars */

import Vue from 'vue';
import Notifications from 'vue-notification';

import breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import login from './components/bootstrap/login.vue';
import modalwindow from './components/bootstrap/modalwindow.vue';
import projectlist from './components/bootstrap/projectlist.vue';
import titlebar from './components/bootstrap/titlebar.vue';
import userprofile from './components/bootstrap/userprofile.vue';

const componentsConfig = {
  titlebar,
  breadcrumbs,
  login,
  modalwindow,
  projectlist,
  userprofile,
};

const createApp = (elementId, template) => {
  Vue.use(Notifications);
  return new Vue({
    el: `#${elementId}`,
    template,
    components: componentsConfig,
  });
};

export default createApp;
