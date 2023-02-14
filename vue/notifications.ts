import { NotificationsOptions, notify } from '@kyvg/vue3-notification';

const showNotification = (title: string, text: string, type = 'info') => {
  notify({
    title,
    text,
    type,
    data: {
      onNotificationClose: (item: any, closeFunction: any) => {
        closeFunction();
      },
    },
  });
};

const showMaintenanceNotification = (noticeItem: any, rangeId: any, closeCallback:any = null) => {
  const duration = -1;
  const delayed = new Date(noticeItem.delayed_to_timestamp * 1000);
  notify({
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
      onNotificationClose: (item: any, closeFunction: Function, fromClick: boolean) => {
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

const showGeneralErrorNotification = (text: string) => {
  const options: NotificationsOptions = {
    // title: window.gettext('Error'), // jshint ignore:line
    title: 'Error',
    type: 'error',
    data: {
      onNotificationClose: (item: any, closeFunction: Function) => {
        closeFunction();
      },
    },
  };
  if (text) {
    options.text = text;
  }
  notify(options);
};

export { showNotification, showGeneralErrorNotification, showMaintenanceNotification };
