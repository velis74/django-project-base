from django_project_base.settings_parser import parse_settings

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


def set_django_project_base_settings():
    parse_settings(DJANGO_PROJECT_BASE_SETTINGS)
