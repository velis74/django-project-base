import Vue from 'vue';
import Notifications from 'vue-notification';
import _ from 'lodash';

const registerComponent = (componentId, componentDefinition) => {
  return Vue.component(componentId, componentDefinition);
};

const createApp = (elementId, mainComponentDefnition) => {
  registerComponent(mainComponentDefnition.id, mainComponentDefnition.definition);
  _.each(mainComponentDefnition.childComponentsDefinition, c => {
    registerComponent(c.id, c.definition);
  });
  Vue.use(Notifications);
  Vue.config.productionTip = false;

  return new Vue({
    el: `#${elementId}`,
  });
};

export {createApp, registerComponent};
