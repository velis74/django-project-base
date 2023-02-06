const createEvent = (id, detail) => new CustomEvent(id, { detail });

const loginEvent = new CustomEvent('login', {});
const logoutEvent = new CustomEvent('logout', {});
const projectSelected = new CustomEvent('project-selected', {});
const maintenanceNotificationAcknowledged = new CustomEvent('maintenance-notification-acknowledged', {});

export { loginEvent, logoutEvent, projectSelected, maintenanceNotificationAcknowledged, createEvent };
