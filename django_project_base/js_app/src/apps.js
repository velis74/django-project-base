// eslint-disable-next-line import/no-extraneous-dependencies
import ModalHandler from 'dynamicforms/src/components/modalhandler.vue';
import Vue from 'vue';

// Dokler nimamo npm packageja je najbolje, da se dynamicforms poveže preko npm link-a:
//  - Na dynamicforms narediš "npm run build", in "npm link"
//  - Na django project base narediš "npm link dynamicforms"
// Potem bi moralo delati

import Breadcrumbs from './components/bootstrap/breadcrumbs.vue';
import Login from './components/bootstrap/login.vue';
import ProjectList from './components/bootstrap/projectlist.vue';
import TitleBar from './components/bootstrap/titlebar.vue';
import UserProfile from './components/bootstrap/userprofile.vue';
import BrowserCheck from './components/browser-check.vue';
import Notification from './components/notification.vue';

const componentsConfig = {
  TitleBar,
  Breadcrumbs,
  Login,
  ProjectList,
  UserProfile,
  Notification,
  BrowserCheck,
};

const createApp = (elementId, template, modalId) => {
  // eslint-disable-next-line no-unused-vars,no-var
  var $buoop = {
    required: {
      e: -4, f: -3, o: -3, s: -1, c: -3,
    },
    insecure: true,
    api: 2022.01,
  };

  // eslint-disable-next-line camelcase
  function $buo_f() {
    const e = document.createElement('script');
    e.src = '//browser-update.org/update.min.js';
    document.body.appendChild(e);
  }

  try {
    document.addEventListener('DOMContentLoaded', $buo_f, false);
  } catch (e) {
    window.attachEvent('onload', $buo_f);
  }

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
  return new Vue({
    el: `#${elementId}`,
    components: componentsConfig,
    template,
  });
};

export default createApp;
