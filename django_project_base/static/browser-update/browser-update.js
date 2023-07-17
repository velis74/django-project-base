var $buoop = {
  required: {
    e: -4,
    f: -4,
    o: -4,
    s: -4,
    c: -4,
  },
  insecure: true,
  unsupported: true,
  reminder: 0,
  reminderClosed: 1,
  noclose: true,
};

window.$buoop = $buoop;

function $buo_f() {
  var e = document.createElement("script");
  e.src = "/static/browser-update/update.min.js";
  document.body.appendChild(e);
}

document.addEventListener("DOMContentLoaded", $buo_f, false);
