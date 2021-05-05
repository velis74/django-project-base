/* eslint-disable no-undef */
/* eslint-disable import/prefer-default-export */
const translate = (name) => {
  if (typeof gettext === 'undefined') {
    return name;
  }
  return gettext(name); // jshint ignore:line
};

export { translate };
