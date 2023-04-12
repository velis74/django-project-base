Profile
=======

Account / profile API.

Django project base uses multi-table inheritance together with abstract base classes to provide boilerplate user
profile fields. The goal of our profile was to provide some social aspects as well as cover small communities where
personal details like phone numbers are more commonly used as means of communication. Of course, any of the fields may
be freely skipped with customisation.

Profile reverse name order
--------------------------

Settings option **PROFILE_REVERSE_FULL_NAME_ORDER** defines first_name, last_name order for readonly field *full_name*.
Default order is *False* - "First Last". Changing setting to true will reverse order to "Last First".

Global setting can be also overrided with profile option reverse_full_name_order (bool).

Deleting profile
----------------

Super admins can either delete profile or mark it for deletion in future.

User cannot delete their profile, they can only mark it for deletion in future. After confirmation for deletion, their
profile is marked for deletion, user is logged out and is not able to log in or use features that require logged in
user.

Settings value **DELETE_PROFILE_TIMEDELTA** defines how far in future user profile will be actually deleted with
automatic process. Value is set in days. The intent is in keeping user data in case they change their mind and
re-register.

Existing profile table troubleshooting
--------------------------------------

You may find yourself in a pinch if your project already has a user profile table and it's not linked to
django.auth.User model using multi-model inheritance. Instead, you might have implemented it with a separate
OneToOneField or even a ForeignKey. Even worse, if you linked all the user fields to this model and not the
django.auth.User model.

You are SOL: migration will not be a matter of extending the model, but rather one of REPLACING the model. It is,
however, only a 4-step (optionally 5-step) process in terms of migrations:

1. Declare the new user profile model, new foreign keys to the profile model in all tables where you link to your
   existing model. Basically you have duplicated all the fields and the model. run `makemigrations`.
2. Create a new `runPython` migration where you copy all the values from existing fields to new fields. This cannot
   be done in the first migration, you will just get `an error <https://stackoverflow.com/questions/12838111>`_
   running it.

   a. if your references to previous profile model were to its own ID and not to django.auth.User model ID, you will
      have to also perform the translations between the two ID fields. Should be relatively easy in you migration code,
      something like:

      .. code-block:: python

        # assumes you had a relation named "user" in your profile table
        model.objects.update(**{
            field_name + '_new': Subquery(model.objects.filter(pk=OuterRef('pk')).values(field_name + '__user')[:1])
        })

3. Delete all the old fields and model
4. Rename all the new fields and remove pre/postfixes. Optionally rename the new model as well, but don't forget to keep
   the database table name (`class Meta: db_table = 'module_model'`).
5. If you decided not to rename everything back to original names, you will need to replace all the references
   throughout your code. If you're not into `DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_, you might
   consider renaming as a less painful option. Having tests wiull help A LOT here.

You will now end up with a new model that replaces your old one. Of course, the entire procedure is only worth it if you
have code from project base you like and would like to take advantage of. Code such as user merging, maintenance,
profile editor, etc. Regardless, it's a pain taking a bit of time to solve. On the plus side: it's an opportunity for a
bit of a refactoring that's long overdue anyway :D Actually this was written as I (one of the authors of the library)
was converting one of our oldest projects to the new system. I think I just despaired and moaned for a couple of days
before actually doing it in about two hours (I decided NOT to rename the new model and took advantage of the refactoring
opportunity)...
