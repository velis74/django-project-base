Cookie notice component
=======================

Some general guidelines for implementing cookie notice (check regulations for your needs):

- before storing or accessing information on user's device informed user's consent is required

 - users must be informed that the site uses cookies

 - clearly explain how cookies work and how they are being used

 - provide link to a cookie policy or make details for cookie purposes, usage.




For cookie notice component https://github.com/orestbida/cookieconsent libarary is integrated. See library
documentation for defining cookie notification settings.
Component can be used as a standalone Vue application:

.. code-block:: javascript

    <html>
        <head>
            ...
            <script type="application/javascript" src="{% static 'django-project-base/js/django-project-base-vendors.js' %}"></script>
            ...
        <body>
            ...
        </body>
        <script>
            var opt = {
                /* options listed in cookieconsent library page */
            };

            createApp('cookie', '<CookieNotice/>', 'modal-app', opt);
        </script>
    ...

Or component can be used as Vue single file component:

.. code-block:: javascript

    <template>
        ...
        <CookieNotice :options="options"/>
    </template>

    <script>
    import CookieNotice from './components/cookie-notice.vue';

    export default {
        name: 'TitleBar',
        components: {
            CookieNotice,
        },
        data() {
            return {
                options: {
                    /* options listed in cookieconsent library page */
                },
            };
        },
    };
    </script>


