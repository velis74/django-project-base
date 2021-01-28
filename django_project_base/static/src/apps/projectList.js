import Vue from 'vue';
import Notifications from 'vue-notification';
import {projectListComponentDefinition} from '../definitions/projectList';

Vue.use(Notifications);

let ProjectList = null;

if (document.getElementById('django-project-base-project-list-app')) {
  Vue.component(projectListComponentDefinition.defaultId, projectListComponentDefinition.definition);

  ProjectList = new Vue({
    el: '#django-project-base-project-list-app',
  });
}

export default {ProjectList};