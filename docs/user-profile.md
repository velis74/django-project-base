# User profile

## Introduction

Django project base uses multi-table inheritance together with abstract base classes to provide boilerplate user profile
fields. The goal of our profile was to provide some social aspects as well as cover small communities where personal
details like phone numbers are more commonly used as means of communication. Of course, any of the fields may be freely
skipped with customisation.

## Impersonate user

Impersonate user functionality is a useful tool for administrators with sufficient privileges to temporarily access and
interact with a system as if they were a different user. This feature can be used for troubleshooting or investigating
issues on behalf of the user.

To enter impersonate user mode, the administrator must navigate to the "Impersonate user" menu and select the user they
wish to impersonate. They can then click on the "Impersonate" button to start the process.

While in impersonate user mode, the administrator will have access to all the same functionality as the user being
impersonated, including viewing their account information, accessing their settings and preferences, and performing
actions on their behalf. It is important to note that the administrator will be acting as the user during this time, so
any actions taken will be recorded as having been performed by the user.

To exit impersonate user mode, the administrator can click on the "Stop impersonation" menu. It is important to always
use this feature responsibly and with the user's permission and to act within the boundaries of the law and ethical
standards.

In addition to using the UI for impersonating a user, user change is also supported via REST API calls or the
userProfile component. The functionality is based on the django-hijack package, and you can set your own logic for
determining which user can impersonate which user. By default, only superusers are allowed to hijack other users.

Here is an example of how to set the authorization check function in the settings file and define the logic for
determining whether a user is authorized to hijack another user:

```python

# settings.py
HIJACK_AUTHORIZATION_CHECK = 'app.utils.authorization_check'


# app.utils.py
def authorization_check(hijacker, hijacked):
    """
    Checks if a user is authorized to hijack another user
    """
    if my_condition:
        return True
    else:
        return False
```

Remember to use this feature responsibly and only with the user's permission and within the boundaries of the law and
ethical standards.

## Deleting profile

Super admins can either delete profile or mark it for deletion in future.

User cannot delete their profile, they can only mark it for deletion in future. After confirmation for deletion, their
profile is marked for deletion, user is logged out and is not able to log in or use features that require logged in
user.

Additionally, take a look at the DELETE_PROFILE_TIMEDELTA settings value.

## Merging user profiles

Sometimes users create multiple accounts. This is undesirable and Django Project Base offers solution for merging user 
accounts.
From Django Project Base Components library you can use \<merge-users\/\> Vue component which will provide a UI for merging 
users.

UI for merging users is composed from two tables 

|User Profiles Table|Users To Be Merged Table|
|--|--|
|<table> <tr><th>Column 1</th><th>Column 2</th></tr><tr><td>Row 1 Column 1</td><td>Row 1 Column 2</td></tr> </table> | <table> <tr><th>Column 2</th><th>Column 1</th></tr><tr><td>Row 1 Column 1</td><td>Row 1 Column 2</td></tr> </table>|

We find user in User Profiles Table and with row action(click on merge button) we add user to right-hand side table. When we 
add all users we want to merge to one account we click on merge button in "Users To Be Merged Table" header and when 
user logs in with one of the accounts in group we created then logic for merging users is executed. Function/logic for 
merging users is set with MERGE_USERS_HANDLER setting.

## Settings

### DJANGO_PROJECT_BASE_PROFILE_MODEL

```python
DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'
```

Set swappable model for Django project base Profile model.

### DELETE_PROFILE_TIMEDELTA

```python
DELETE_PROFILE_TIMEDELTA = 0
``` 

Settings value **DELETE_PROFILE_TIMEDELTA** defines how far in future user profile will be actually deleted with
automatic process. Value is set in days. The intent is in keeping user data in case they change their mind and
re-register.

Default value is 0.

### PROFILE_REVERSE_FULL_NAME_ORDER

```python
PROFILE_REVERSE_FULL_NAME_ORDER = False
``` 

Settings option **PROFILE_REVERSE_FULL_NAME_ORDER** defines first_name, last_name order for readonly field *full_name*.
Default order is *False* - "First Last". Changing setting to true will reverse order to "Last First".

Global setting can be also overrided with profile option reverse_full_name_order (bool).

Default value is False.

### USER_CACHE_KEY

```python
USER_CACHE_KEY = 'django-user-{id}'
```

Key name for user caching background. Default value is 'django-user-{id}'.

### CACHE_IMPERSONATE_USER

```python
CACHE_IMPERSONATE_USER = 'impersonate-user-%d'
```

Cache key name for impersonate user. Default value is 'impersonate-user-%d'.

## Troubleshooting

### Existing profile table troubleshooting

You may find yourself in a pinch if your project already has a user profile table and it's not linked to
django.auth.User model using multi-model inheritance. Instead, you might have implemented it with a separate
OneToOneField or even a ForeignKey. Even worse, if you linked all the user fields to this model and not the
django.auth.User model.

You are SOL: migration will not be a matter of extending the model, but rather one of REPLACING the model. It is,
however, only a 4-step (optionally 5-step) process in terms of migrations:

1. Declare the new user profile model, new foreign keys to the profile model in all tables where you link to your
   existing model. Basically you have duplicated all the fields and the model. run `makemigrations`.
2. Create a new `runPython` migration where you copy all the values from existing fields to new fields. This cannot be
   done in the first migration, you will just get `an error <https://stackoverflow.com/questions/12838111>`_
   running it.

   a. if your references to previous profile model were to its own ID and not to django.auth.User model ID, you will
   have to also perform the translations between the two ID fields. Should be relatively easy in you migration code,
   something like:

```python
# assumes you had a relation named "user" in your profile table
model.objects.update(**{
        field_name + '_new': Subquery(model.objects.filter(pk=OuterRef('pk')).values(field_name + '__user')[:1])
})
```

3. Delete all the old fields and model
4. Rename all the new fields and remove pre/postfixes. Optionally rename the new model as well, but don't forget to keep
   the database table name (`class Meta: db_table = 'module_model'`).
5. If you decided not to rename everything back to original names, you will need to replace all the references
   throughout your code. If you're not into `DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_, you might
   consider renaming as a less painful option. Having tests will help A LOT here.

You will now end up with a new model that replaces your old one. Of course, the entire procedure is only worth it if you
have code from project base you like and would like to take advantage of. Code such as user merging, maintenance,
profile editor, etc. Regardless, it's a pain taking a bit of time to solve. On the plus side: it's an opportunity for a
bit of a refactoring that's long overdue anyway :D Actually this was written as I (one of the authors of the library)
was converting one of our oldest projects to the new system. I think I just despaired and moaned for a couple of days
before actually doing it in about two hours (I decided NOT to rename the new model and took advantage of the refactoring
opportunity)...

