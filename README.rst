What is django-project-settings?
================================

We start with a project. Everything revolves around it: users, roles, permissions, tags, etc. Everything belongs to a
project first, then to database. This project makes it easy to work on that premise. At the same time it integrates a
few basic operations that you need in every project so that you don't have to do them over and over again.

This is a `django <https://www.djangoproject.com/>`_ library, based on
`django-rest-framework <https://www.django-rest-framework.org/>`_ with
`django-allauth <https://github.com/pennersr/django-allauth>`_ integration.


Why django-project-settings?
============================

Functionalities provided:

* A base Project definition and editor for it. Extend as you like.
* User profile editor. Manage emails, confirmations, social connections
* Support for REST-based authentication / session creation
* Session / user caching for speed
* Project users editor. Invite users to project. Assign them into roles.
* Roles management & rights assignment.
* Tags editor & manager + support API for marking tagged items with their colours or icons
