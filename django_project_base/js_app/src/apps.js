// eslint-disable-next-line import/no-extraneous-dependencies
import ModalHandler from 'dynamicforms/src/components/modalhandler.vue';
import Vue from 'vue';
import Notifications from 'vue-notification';

// Dokler nimamo npm packageja je najbolje, da se dynamicforms poveže preko npm link-a:
//  - Na dynamicforms narediš "npm run build", in "npm link"
//  - Na django project base narediš "npm link dynamicforms"
// Potem bi moralo delati

import Breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import Login from './components/bootstrap/login.vue';
import ProjectList from './components/bootstrap/projectlist.vue';
import TitleBar from './components/bootstrap/titlebar.vue';
import UserProfile from './components/bootstrap/userprofile.vue';

const componentsConfig = {
  TitleBar,
  Breadcrumbs,
  Login,
  ProjectList,
  UserProfile,
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
    components: componentsConfig,
    template,
  });
};

export default createApp;
