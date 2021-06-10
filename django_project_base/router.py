from django_project_base.base.rest.router import Router as ProjectBaseRouter
from django_project_base.constants import ACCOUNT_URL_PREFIX
from django_project_base.rest.impersonate import ImpersonateUserViewset
from django_project_base.rest.profile import ProfileViewSet
from django_project_base.rest.project import ProjectViewSet


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
