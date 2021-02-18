import Vue from 'vue';
import Notifications from 'vue-notification';
import _ from 'lodash';

const registerComponent = (componentId, componentDefinition) => {
  return Vue.component(componentId, componentDefinition);
};

const createApp = (elementId, mainComponentDefnition) => {
  _.each(mainComponentDefnition.childComponentsDefinition, c => {
    _.each(c.childComponentsDefinition, _c => {
      registerComponent(_c.id, _c.definition);
    });
    registerComponent(c.id, c.definition);
  });
  registerComponent(mainComponentDefnition.id, mainComponentDefnition.definition);
  Vue.use(Notifications);
  Vue.config.productionTip = false;

  return new Vue({
    el: `#${elementId}`,
  });
};

export {createApp, registerComponent};
