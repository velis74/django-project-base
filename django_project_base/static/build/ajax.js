'use strict';

(function () {
  'use strict';

  var Ajax = {
    loading: false,
    request: function request(url, options) {
      var o = {
        data: null,
        success: function success() {},
        failure: function failure() {},
        always: function always() {},
        beforeSend: function beforeSend() {},
        headers: {},
        type: 'POST',
        loading: true,
        stopLoading: true,
        overlay: false,
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        processData: true,
        async: true
      };
      $.extend(o, options);

      if (!o.data && o.type === 'POST') {
        //request with no data is GET request
        o.data = null;
        o.type = 'GET';
      }

      $.ajax({
        url: url,
        type: o.type,
        data: o.data,
        beforeSend: function beforeSend(xhr) {
          o.beforeSend(xhr);
        },
        cache: false,
        processData: o.processData,
        contentType: o.contentType,
        headers: o.headers,
        async: o.async
      }).done(function (result) {
        o.success(result);
      }).fail(function (xhr) {
        // redirect to login if user session has expired
        if (xhr.status === 401) {
          setTimeout(function () {
            window.location.href = '/'; //todo: redirect to login
          }, 2500);
        }
        o.failure(xhr.responseJSON, xhr.status);
      }).always(function (xhr) {
        Ajax.loading = false;
        o.always(xhr);
      });
    }
  };

  window.Ajax = Ajax;

  $.ajaxPrefilter(function (options, originalOptions, xhr) {
    // this will run before each request
    var token = null; //todo: read token

    if (token) {
      return xhr.setRequestHeader('X-CSRF-TOKEN', token);
    }
  });
})();