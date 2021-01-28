import Vue from 'vue';
import Notifications from 'vue-notification';
import {breadcrumbsComponentDefinition} from '../../definitions/breadcrumbs';
import {projectListComponentDefinition} from '../../definitions/projectList';
import {titlebarComponentDefinition} from '../../definitions/titlebar';
import {loginComponentDefinition} from '../../definitions/login';
import {userProfileComponentDefinition} from '../../definitions/userProfile';

Vue.use(Notifications);

let TitleBar = null;

if (document.getElementById('django-project-base-titlebar-app')) {
  Vue.component(titlebarComponentDefinition.defaultId, titlebarComponentDefinition.definition);
  Vue.component(breadcrumbsComponentDefinition.defaultId, breadcrumbsComponentDefinition.definition);
  Vue.component(projectListComponentDefinition.defaultId, projectListComponentDefinition.definition);
  Vue.component(loginComponentDefinition.defaultId, loginComponentDefinition.definition);
  Vue.component(userProfileComponentDefinition.defaultId, userProfileComponentDefinition.definition);

  TitleBar = new Vue({
    el: '#django-project-base-titlebar-app',
  });
}

export default {TitleBar};