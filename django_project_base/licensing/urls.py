from django.urls import include, path

from django_project_base.licensing.rest.router import licensing_router

urlpatterns = [
    path("", include(licensing_router.urls)),
]
