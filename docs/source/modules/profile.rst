Profile
=======

Account / profile API.

Profile reverse name order
--------------------------

Settings option **PROFILE_REVERSE_FULL_NAME_ORDER** defines first_name, last_name order for readonly field *full_name*.
Default order is *False* - "First Last". Changing setting to true will reverse order to "Last First".

Global setting can be also overrided with profile option reverse_full_name_order (bool).

Deleting profile
----------------

Super admins can either delete profile or mark it for deletion in future.

User cannot delete its profile, he can only mark it for deletion in future. After confirmation for deletion, his profile
is marked for deletion, user is logged out and is not able to log in or use features that require logged in user.

Settings value **DELETE_PROFILE_TIMEDELTA** defines  how far in future will user profile be actually deleted with
automatic process. Value is set in days.