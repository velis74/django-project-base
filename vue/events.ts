const createEvent = (id: any, detail: any) => new CustomEvent(id, { detail });

const logoutEvent = new CustomEvent('logout', {});
const projectSelected = new CustomEvent('project-selected', {});
const maintenanceNotificationAcknowledged = new CustomEvent('maintenance-notification-acknowledged', {});

export { logoutEvent, projectSelected, maintenanceNotificationAcknowledged, createEvent };
