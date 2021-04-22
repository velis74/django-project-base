Django project base user account management
###########################################

Django project base offers basic account management out of the box. Please look
at `Swagger Accounts </schema/swagger-ui/#/account>`_


Social integrations
___________________

Django Project Base offers easy-to-setup social authentication mechanism. Currently the following providers are
supported:

 - Facebook
    - provider identifier: facebook
 - Google
    - provider identifier: google-oauth2
 - Twitter
    - provider identifier: twitter
 - Microsoft
    - provider identifier: microsoft-graph
 - Github
    - provider identifier: github
 - Gitlab
    - provider identifier: gitlab

OAuth providers require redirect URL which is called after the authentication process in Oauth flow.

Your redirect url is: [SCHEME]://[HOST]/account/social/complete/[PROVIDER IDENTIFIER]/

Information which settings are required for a social provider can be
found at https://python-social-auth.readthedocs.io/en/latest/backends/index.html

For social authentication functionalities `Python Social Auth <https://python-social-auth.readthedocs.io>`_ library
was used. Please checkout this documentation to make any custom changes.


**Installation**

 Add app to your installed apps.

 .. code-block:: python

    # myproject/settings.py

    from django_project_base.accounts import ACCOUNT_APP_ID

    INSTALLED_APPS = [
        ...
        ACCOUNT_APP_ID,
     ]


 Make sure you have django project base urls included:

 .. code-block:: python

    # url.py

    urlpatterns += django_project_base_urlpatterns


 Run migrations:

 .. code-block:: python

    python manage.py migrate


**Social login integration example - Google**

To enable a social provider create an account at provider webpage and create an oauth app. For example for Google OAuth
login visit https://console.developers.google.com/apis/credentials. Click + CREATE CREDENTIALS and select
Oauth Client ID. Then create OAuth app with OAuth Consent screen.

Example value for Authorized JavaScript origins can be http://localhost:8080.

Example value for Authorized redirect URIs can be http://localhost:8080/account/social/complete/google-oauth2/.

To enable Google OAuth login add folowing to settings:

 .. code-block:: python

    # myproject/settings.py
    # enable google social login
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '*Client ID*'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '*Client secret*'


 .. code-block:: HTML

     <!DOCTYPE html>
     <html lang="en">
         <head>
             <meta charset="UTF-8">
             <title>Google login example</title>
         <body>
            <div>
                <button>
                    <a href="/account/social/login/google-oauth2/">Login with Google social provider</a>
                </button>
            </div>
        </body>
     </html>