import Vue from 'vue';

const showNotification = (title, text, type = 'info') => {
  Vue.notify({
    title: title,
    text: text,
    type: type
  });
};

const showGeneralErrorNotification = (text) => {
  let options = {
    title: gettext('Error'), // jshint ignore:line
    type: 'error'
  };
  if (!!text) {
    options.text = text;
  }
  Vue.notify(options);
};

export {showNotification, showGeneralErrorNotification};