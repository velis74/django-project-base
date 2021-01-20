from django.conf.urls import url
from django.urls import path, include

from django_project_base.base.rest.project_base_router import ProjectBaseRouter
from django_project_base.rest.profile import ProfileViewSet
from django_project_base.rest.project import ProjectViewSet


class RestRouter(ProjectBaseRouter):
    pass


django_project_base_router = RestRouter(trailing_slash=False)
django_project_base_router.register(r'project', ProjectViewSet, basename='project-base-project')
django_project_base_router.register(r'profile', ProfileViewSet, basename='profile-base-project')

django_project_base_urlpatterns = [
    path('dpb-rest-accounts/', include('rest_registration.api.urls')),
    url(r'dpb-rest/', include(django_project_base_router.urls)),
]
