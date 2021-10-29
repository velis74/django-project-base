import Vue from 'vue';

const showNotification = (title, text, type = 'info') => {
  Vue.notify({
    title,
    text,
    type,
    data: {
      onNotificationClose: (item, closeFunction) => {
        closeFunction();
      },
    },
  });
};

const showMaintenanceNotification = (noticeItem, rangeId, closeCallback = null) => {
  const duration = -1;
  const delayed = new Date(noticeItem.delayed_to_timestamp * 1000);
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
    duration,
    type: 'error',
    data: {
      onNotificationClose: (item, closeFunction, fromClick) => {
        if (fromClick) {
          return;
        }
        if (closeCallback) {
          closeCallback();
        }
        closeFunction();
      },
      id: noticeItem.id,
      duration,
    },
  });
};

const showGeneralErrorNotification = (text) => {
  const options = {
    title: window.gettext('Error'), // jshint ignore:line
    type: 'error',
    data: {
      onNotificationClose: (item, closeFunction) => {
        closeFunction();
      },
    },
  };
  if (text) {
    options.text = text;
  }
  Vue.notify(options);
};

export { showNotification, showGeneralErrorNotification, showMaintenanceNotification };
