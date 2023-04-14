# Introduction

## What is django-project-base?

This project removes the boilerplate associated with project / user handling: We start with a project. Everything
revolves around it: users, roles, permissions, tags, etc. This project makes it easy to work on that premise: it
provides foundations for user profiles, oauth authentication, permissions, projects, tagging, etc.

In order to take advantage of all this, just enable desired middleware and extend the models. This project will take
care of the groundwork while you focus on your own project.

This is a django library, based on django-rest-framework with DynamicForms and Django REST Registration integration.

## Why django-project-base?

Functionalities provided:

- A base Project definition and editor for it. Extend as you like.
- User profile editor. Manage emails, confirmations, social connections
- Support for REST-based authentication / session creation
- Session / user caching for speed
- Project users editor. Invite users to project. Assign them into roles.
- Roles management & rights assignment.
- Tags editor & manager + support API for marking tagged items with their colours or icons
- Various Vue components for visualising the above in browsers
