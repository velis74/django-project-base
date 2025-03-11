import { DfNotifications, interpolate } from '@velis/dynamicforms';

const showNotification = (
  title: string,
  text: string,
  type = 'info',
  duration: number | undefined = undefined,
  id: number | undefined = undefined,
) => {
  DfNotifications.showNotification(title, text, type, duration, id);
};

const showMaintenanceNotification = (noticeItem: any, rangeId: any, closeCallback: any = null) => {
  const duration = -1;
  const delayed = new Date(noticeItem.delayed_to * 1000);
  DfNotifications.showNotification(
    noticeItem.message.subject,
    interpolate('%(body)s<br>%(footer)s<br><br>Maintenance starts at: %(delayed)s', {
      body: noticeItem.message.body,
      footer: noticeItem.message.footer,
      delayed,
    }),
    'error',
    duration,
    undefined,
    {
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
  );
};

const showGeneralErrorNotification = (text: string) => {
  DfNotifications.showErrorNotification(text);
};

const closeNotification = (id: number) => {
  DfNotifications.closeNotification(id);
};

export { showNotification, showGeneralErrorNotification, showMaintenanceNotification, closeNotification };
