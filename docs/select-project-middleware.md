# Select project middleware

SelectProjectMiddleware keeps track of currently selected project, and it is mandatory in django project base.

Project is selected based on 
[DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE](./project.md#django_project_base_selected_project_mode)

## Currently selected project

if setting `DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE` is set to `SelectedProjectMode.FULL`, project is selected 
according to the `DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES` setting, specifically the "project" section.

if setting `DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE` is set to `SelectedProjectMode.PROMPT`, project is selected 
according to user permissions. So in this case `request` needs to have `user` attribute that is set in 
`django.contrib.auth.middleware.AuthenticationMiddleware`. This means that 
`django.contrib.auth.middleware.AuthenticationMiddleware` must be executed before `SelectProjectMiddleware`.

SelectProjectMiddleware will be keeping track of currently selected project and the
following variable will become available for use:

```python
request.selected_project
```

It is a `SimpleLazyObject` resolving to currently selected project. The information is also written in the
session data, so not every API call needs to bear project slug in order for the system to know it.

If selected_project cannot evaluate, either because the setting is not set or because the project can't be found,
a `ProjectNotSelectedError` will be raised. The exception derives from `NotImplementedError`, but has a `message` member
in case you might want to throw a more API-friendly error with the same message. DPB itself does this on several 
occasions transforming a `ProjectNotSelectedError` into a 404 - `NotFound`.

Also note that SimpleLazyObject does not evaluate simply by invoking it, e.g. `request.selected_project`. You actually 
have to access one of its members, e.g. 
`request.selected_project.get_deferred_fields()  # force immediate LazyObject evaluation`. If you're trying to catch 
the exception, make sure you force evaluation. There are examples for both forced and "natural" evaluation in DPB code.

