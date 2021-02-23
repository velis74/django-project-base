import Vue from 'vue';
import Notifications from 'vue-notification';
import _ from 'lodash';

const registerComponent = (componentId, componentDefinition) => {
  if (componentDefinition.childComponentsDefinition && componentDefinition.childComponentsDefinition.length > 0) {
    _.each(componentDefinition.childComponentsDefinition, ch => {
      return registerComponent(ch.id, ch);
    });
  }
  Vue.component(componentId, componentDefinition.definition);
};

const createApp = (elementId, mainComponentDefnition) => {
  registerComponent(mainComponentDefnition.id, mainComponentDefnition);
  Vue.use(Notifications);
  Vue.config.productionTip = false;

  return new Vue({
    el: `#${elementId}`,
  });
};

export {createApp, registerComponent};
