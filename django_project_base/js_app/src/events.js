(function () {
  if (typeof window.CustomEvent === "function") return false; //If not IE

  function CustomEvent(event, params) {
    params = params || {bubbles: false, cancelable: false, detail: undefined};
    var evt = document.createEvent('CustomEvent');
    evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
    return evt;
  }

  CustomEvent.prototype = window.Event.prototype;

  window.CustomEvent = CustomEvent;
})();

const createEvent = (id, detail) => {
  return new CustomEvent(id, {detail: detail});
};

const loginEvent = new CustomEvent('login', {});
const logoutEvent = new CustomEvent('logout', {});
const projectSelected = new CustomEvent('project-selected', {});

export {loginEvent, logoutEvent, projectSelected, createEvent};