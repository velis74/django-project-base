import Vue from 'vue';
import Notifications from 'vue-notification';
import {loginComponentDefinition} from '../definitions/login';

Vue.use(Notifications);
Vue.config.productionTip = false;

let Login = null;

if (document.getElementById('django-project-base-login-app')) {
  Vue.component(loginComponentDefinition.defaultId, loginComponentDefinition.definition);

  Login = new Vue({
    el: '#django-project-base-login-app',
  });
}

export default {Login};