VUE components
==============

Project base currently supports a few components for visualisation of the exposed APIs.

The components are designed to be customisable making it easy to replace any subcomponents with your own.

Here's the overview of the built-in components:

.. toctree::
   :maxdepth: 2
   :name: vuetoc

   vue-titlebar
   vue-cookie-notice

Vue single file components
--------------------------

You can add django_project_base as a js library to your package.json when developing Vue projects.

**Notifications**

If you want to use notifications django project base integrates vue-notification library. If you are not using django project
base components you can add notifications by adding <Notification/> component in your App.vue or other component if you wish to use notifications functionality.
