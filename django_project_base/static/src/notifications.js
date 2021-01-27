import Vue from 'vue';
import {translationData} from './translations';

const showNotification = (title, text, type = 'info') => {
  Vue.notify({
    title: title,
    text: text,
    type: type
  });
};

const showGeneralErrorNotification = () => {
  Vue.notify({
    title: translationData['general-error'],
    type: 'error'
  });
};

export {showNotification, showGeneralErrorNotification};