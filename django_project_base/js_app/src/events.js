// eslint-disable-next-line consistent-return
(function () {
  if (typeof window.CustomEvent === 'function') return false; // If not IE

  function CustomEvent(event, params) {
    // eslint-disable-next-line no-param-reassign
    params = params || { bubbles: false, cancelable: false, detail: undefined };
    const evt = document.createEvent('CustomEvent');
    evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
    return evt;
  }

  CustomEvent.prototype = window.Event.prototype;

  window.CustomEvent = CustomEvent;
}());

const createEvent = (id, detail) => new CustomEvent(id, { detail });

const loginEvent = new CustomEvent('login', {});
const logoutEvent = new CustomEvent('logout', {});
const projectSelected = new CustomEvent('project-selected', {});
const maintenanceNotificationAcknowledged = new CustomEvent('maintenance-notification-acknowledged', {});

export {
  loginEvent, logoutEvent, projectSelected, maintenanceNotificationAcknowledged, createEvent,
};
