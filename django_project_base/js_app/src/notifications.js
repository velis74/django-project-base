import Vue from 'vue';

const showNotification = (title, text, type = 'info') => {
  Vue.notify({
    title: title,
    text: text,
    type: type
  });
};

const showGeneralErrorNotification = () => {
  Vue.notify({
    title: gettext('Error'), // jshint ignore:line
    type: 'error'
  });
};

export {showNotification, showGeneralErrorNotification};