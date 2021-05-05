DJANGO_PROJECT_BASE_SETTINGS = (
    {
        "name": "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES",
        "default": {'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
                    'language': {'value_name': 'current_language', 'url_part': 'language-'}},
    },
    {
        "name": "DJANGO_PROJECT_BASE_SLUG_FIELD_NAME",
        "default": "slug",
    },

)

MIDDLEWARE = [
    'ScantronServer.profile_middleware.profile_middleware',
]

CACHE_IMPERSONATE_USER = 'impersonate-user-%d'

def set_django_project_base_settings():
    from django.conf import settings
    for _setting in DJANGO_PROJECT_BASE_SETTINGS:
        setattr(settings, _setting["name"], getattr(_setting, _setting["name"], _setting["default"]))
