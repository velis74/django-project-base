import Vue from 'vue';
import {userProfileComponentDefinition} from '../definitions/userProfile';


let UserProfile = null;
Vue.config.productionTip = false;

if (document.getElementById('django-project-base-user-profile-app')) {
  Vue.component(userProfileComponentDefinition.defaultId, userProfileComponentDefinition.definition);

  UserProfile = new Vue({
    el: '#django-project-base-user-profile-app',
  });
}

export default {UserProfile};