from pathlib import Path

from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from django_project_base.base.rest.router import Router as ProjectBaseRouter
from django_project_base.constants import ACCOUNT_URL_PREFIX
from django_project_base.performance_middleware.request_statistics.app_debug_view import app_debug_view
from django_project_base.notifications import NOTIFICATIONS_APP_ID
from django_project_base.notifications.rest.router import notifications_router
from django_project_base.rest.impersonate import ImpersonateUserViewset
from django_project_base.rest.profile import ProfileViewSet
from django_project_base.rest.project import ProjectViewSet
from django_project_base.views import documentation_view
from drf_spectacular.settings import SPECTACULAR_DEFAULTS
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def filter_rest_documentation_endpoints(endpoints: list) -> list:
    _endpoints: list = []
    for (path_, path_regex, method, callback) in endpoints:
        module: str = getattr(getattr(callback, 'view_class', object()), '__module__', '')
        exclude: bool = 'profile' in path_ and 'rest_registration' in module
        if not exclude:
            _endpoints.append((path_, path_regex, method, callback))
    return _endpoints


class RestRouter(ProjectBaseRouter):
    pass


django_project_base_router = RestRouter(trailing_slash=False)
django_project_base_router.register(r'project', ProjectViewSet, basename='project-base-project')
django_project_base_router.register(r'%s/profile' % ACCOUNT_URL_PREFIX, ProfileViewSet, basename='profile-base-project')
django_project_base_router.register(r'%s/impersonate' % ACCOUNT_URL_PREFIX, ImpersonateUserViewset,
                                    basename='profile-base-impersonate-user')

SPECTACULAR_DEFAULTS['TITLE'] = 'Rest documentation'
SPECTACULAR_DEFAULTS['DESCRIPTION'] = 'Api documentation'
SPECTACULAR_DEFAULTS['VERSION'] = '0.0.1'
SPECTACULAR_DEFAULTS['PREPROCESSING_HOOKS'] = [
    'django_project_base.router.filter_rest_documentation_endpoints'
]
documentation_directory: str = str(Path().resolve()) + '/docs/build/'

django_project_base_urlpatterns = [
    path('%s/' % ACCOUNT_URL_PREFIX, include('rest_registration.api.urls')),
    url(r'', include(django_project_base_router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema', ), name='swagger-ui'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^app-debug/', app_debug_view, name='app-debug'),
    url(
        r'^docs-files/(?P<path>.*)$',
        documentation_view, {'document_root': documentation_directory}, name='docs-files'
    ),  # url for sphinx
]

if NOTIFICATIONS_APP_ID in settings.INSTALLED_APPS:
    django_project_base_urlpatterns.append(url(r'', include(notifications_router.urls)))
