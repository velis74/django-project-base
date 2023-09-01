import { NotificationsOptions, notify } from '@kyvg/vue3-notification';
import { gettext } from '@velis/dynamicforms';

const showNotification = (
  title: string,
  text: string,
  type = 'info',
  duration: number | undefined = undefined,
  id: number | undefined = undefined,
) => {
  notify({
    title,
    text,
    duration,
    id,
    type,
    data: {
      onNotificationClose: (item: any, closeFunction: any) => {
        closeFunction();
      },
    },
  });
};

const showMaintenanceNotification = (noticeItem: any, rangeId: any, closeCallback: any = null) => {
  const duration = -1;
  const delayed = new Date(noticeItem.delayed_to * 1000);
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
    title: gettext('Error'),
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

const closeNotification = (id: number) => {
  notify.close(id);
};

export { showNotification, showGeneralErrorNotification, showMaintenanceNotification, closeNotification };
