from django.conf.urls import url
from django.urls import path, include
from drf_spectacular.settings import SPECTACULAR_DEFAULTS
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django_project_base.base.rest.project_base_router import ProjectBaseRouter
from django_project_base.rest.profile import ProfileViewSet
from django_project_base.rest.project import ProjectViewSet


class RestRouter(ProjectBaseRouter):
    pass


django_project_base_router = RestRouter(trailing_slash=False)
django_project_base_router.register(r'project', ProjectViewSet, basename='project-base-project')
django_project_base_router.register(r'profile', ProfileViewSet, basename='profile-base-project')

SPECTACULAR_DEFAULTS['TITLE'] = 'Rest documentation'
SPECTACULAR_DEFAULTS['DESCRIPTION'] = 'Api documentation'
SPECTACULAR_DEFAULTS['VERSION'] = '0.0.1'

django_project_base_urlpatterns = [
    path('dpb-rest-account/', include('rest_registration.api.urls')),
    url(r'dpb-rest/', include(django_project_base_router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
