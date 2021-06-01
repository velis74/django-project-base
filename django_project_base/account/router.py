from django_project_base.base.rest.router import Router as ProjectBaseRouter

from .rest import AccountViewSet

router = ProjectBaseRouter(trailing_slash=True)

router.register(r'', AccountViewSet, basename='login')
