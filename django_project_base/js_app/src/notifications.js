import Vue from 'vue';
import {apiClient as ApiClient} from "./apiClient";

const showNotification = (title, text, type = 'info') => {
  Vue.notify({
    title: title,
    text: text,
    type: type,
    data: {
      onNotificationClose: (item, closeFunction) => {
        closeFunction();
      }
    },
  });
};

const showMaintenanceNotification = (noticeItem) => {
  console.log(noticeItem);
  const duration = -1;
  let delayed = new Date(noticeItem.delayed_to_timestamp * 1000);
  Vue.notify({
    title: noticeItem.message.subject,
    text: `
        ${noticeItem.message.body} 
        <br>  
        ${noticeItem.message.footer}
        <br>
        <br>
        Maintenance starts at: ${delayed} 
    `,
    duration: duration,
    type: 'error',
    data: {
      onNotificationClose: (item, closeFunction, fromClick) => {
        if (fromClick) {
          return;
        }
        ApiClient.post('maintenance-notification/acknowledged/', {
          id: item.data.id,
          minutes_till_maintenance: Math.round((delayed.getTime() - new Date().getTime()) / 60000), // jshint ignore:line
        }).then(() => {
          closeFunction();
        });
      },
      id: noticeItem.id,
      duration: duration,
    },
  });
};

const showGeneralErrorNotification = (text) => {
  let options = {
    title: gettext('Error'), // jshint ignore:line
    type: 'error',
    data: {
      onNotificationClose: (item, closeFunction) => {
        closeFunction();
      }
    },
  };
  if (!!text) {
    options.text = text;
  }
  Vue.notify(options);
};

export {showNotification, showGeneralErrorNotification, showMaintenanceNotification};