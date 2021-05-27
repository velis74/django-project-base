from django_project_base.base.rest.router import Router as ProjectBaseRouter

from .rest import AccountViewSet

accounts_router = ProjectBaseRouter(trailing_slash=True)

accounts_router.register(r'', AccountViewSet, basename='account')
