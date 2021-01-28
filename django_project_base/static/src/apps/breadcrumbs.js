import Vue from 'vue';
import {breadcrumbsComponentDefinition} from '../definitions/breadcrumbs';


let Breadcrumbs = null;
Vue.config.productionTip = false;

if (document.getElementById('django-project-base-breadcrumbs-app')) {
  Vue.component(breadcrumbsComponentDefinition.defaultId, breadcrumbsComponentDefinition.definition);
  Breadcrumbs = new Vue({
    el: '#django-project-base-breadcrumbs-app',
  });
}

export default {Breadcrumbs};