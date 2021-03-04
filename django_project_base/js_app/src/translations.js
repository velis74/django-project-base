const translate = (name) => {
  if (typeof gettext === 'undefined') {
    return name;
  }
  return gettext(name); // jshint ignore:line
};

export {translate};