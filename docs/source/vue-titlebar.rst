TitleBar component
==================

The toolbar component provides the application toolbar containing page title, breadcrumbs, projects overview and account
UI. Each of the subsections is fully customisable, but here's what the built-in components do:

TitleBar
--------

Master component providing the grayed out area at the top of the page. It also provides visualisation for any messages
the user needs to see, e.g. maintenance notices.

Composed of project image, page title, messages toast, breadcrumbs, projects overview and user profile menu.

..file:
   django_project_base/src/components/bootstrap/titlebar.vue

**Props**

.. code-block:: javascript

    darkMode: { type: Boolean, default: false }, // dark mode on when true
    projectlistComponent: { type: String, default: 'ProjectList' }, // specify your own globally registered component
    userprofileComponent: { type: String, default: 'UserProfile' }, // specify your own globally registered component
    breadcrumbsComponent: { type: String, default: 'Breadcrumbs' }, // specify your own globally registered component
    loginVisible: { type: Boolean, default: true }, // if user is not logged in, should we show the login inputs

All the *Component parameters can be left out to use the provided components.

UserProfile
-----------

Handles user menu and associated UX for logging in, out, impersonation, maintaining social connections, credentials,
etc.

You need to enable the `/account/` URLs so that the component can actually do its work. See :ref:`Authentication`.

