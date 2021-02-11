const loginEvent = new CustomEvent('login', {});
const logoutEvent = new CustomEvent('logout', {});
const projectSelected = new CustomEvent('project-selected', {});

export {loginEvent, logoutEvent, projectSelected};