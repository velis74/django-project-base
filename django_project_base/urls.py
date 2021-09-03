from django.conf.urls import url
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from drf_spectacular.settings import SPECTACULAR_DEFAULTS

from django_project_base.account import urls as accounts_router
from django_project_base.router import django_project_base_router

SPECTACULAR_DEFAULTS['TITLE'] = 'Rest documentation'
SPECTACULAR_DEFAULTS['DESCRIPTION'] = 'Api documentation'
SPECTACULAR_DEFAULTS['VERSION'] = '0.0.1'
SPECTACULAR_DEFAULTS['PREPROCESSING_HOOKS'] = [
    'django_project_base.router.filter_rest_documentation_endpoints'
]

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'', include(django_project_base_router.urls)),
    url(r'account', include(accounts_router)),

]
