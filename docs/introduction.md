# Introduction

## What is django-project-base?

Django project base is a library that simplifies project/user handling by removing boilerplate code. The library
operates under the premise that a project is at the center of everything, including users, roles, permissions, tags, and
other related entities. Django project base provides the foundation for user profiles, OAuth authentication,
permissions, projects, tagging, and more, making it easy for developers to focus on their own project.

To use the library, developers can simply enable the desired middleware and extend the models. Django project base will
take care of the groundwork, leaving developers free to focus on their own project. The library is built on
django-rest-framework, with DynamicForms and Django REST Registration integration.

## Why django-project-base?

Functionalities Provided:

- A base project definition and editor that can be extended as needed
- User profile editor for managing emails, confirmations, and social connections
- Support for REST-based authentication and session creation
- Session and user caching for improved speed
- Project users editor for inviting users to a project and assigning them to specific roles
- Roles management and rights assignment
- Tags editor and manager with API support for marking tagged items with colors or icons
- Various Vue components for visualizing the above in web browsers.
