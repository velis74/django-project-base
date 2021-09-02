/* eslint-disable no-unused-vars */

import Vue from 'vue';
import Notifications from 'vue-notification';

// Dokler nimamo npm packageja je najbolje, da se dynamicforms poveže preko npm link-a:
//  - Na dynamicforms narediš "npm run build", in "npm link"
//  - Na django project base narediš "npm link dynamicformscomponents"
// Potem bi moralo delati

// eslint-disable-next-line import/no-extraneous-dependencies
import ModalHandler from 'dynamicformscomponents/src/components/modalhandler.vue';

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

const createApp = (elementId, template, modalId) => {
  if (typeof window.dynamicforms === 'undefined') {
    window.dynamicforms = {};
  }
  if (!window.dynamicforms.dialog && modalId) {
    // eslint-disable-next-line no-new
    new Vue({
      el: `#${modalId}`,
      components: {
        ModalHandler,
      },
      template: '<ModalHandler></ModalHandler>',
    });
  }
  Vue.use(Notifications);
  return new Vue({
    el: `#${elementId}`,
    template,
    components: componentsConfig,
  });
};

export default createApp;
