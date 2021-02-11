import Vue from 'vue';
import Notifications from 'vue-notification';
import _ from 'lodash';

const createApp = (elementId, mainComponentDefnition) => {
  Vue.component(mainComponentDefnition.id, mainComponentDefnition.definition);
  _.each(mainComponentDefnition.childComponentsDefinition, c => {
    Vue.component(c.id, c.definition);
  });
  Vue.use(Notifications);
  Vue.config.productionTip = false;

  return new Vue({
    el: `#${elementId}`,
  });
};

export {createApp};
