from rest_framework.routers import DefaultRouter

from django_project_base.rest.project import ProjectViewSet


def filter_rest_documentation_endpoints(endpoints: list) -> list:
    _endpoints: list = []
    for (path_, path_regex, method, callback) in endpoints:
        module: str = getattr(getattr(callback, 'view_class', object()), '__module__', '')
        exclude: bool = 'profile' in path_ and 'rest_registration' in module
        if not exclude:
            _endpoints.append((path_, path_regex, method, callback))
    return _endpoints


class RestRouter(DefaultRouter):
    pass


django_project_base_router = RestRouter(trailing_slash=False)
django_project_base_router.register(r'project', ProjectViewSet, basename='project-base-project')
