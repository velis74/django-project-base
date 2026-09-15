from django.urls import include, path

from django_project_base.account.router import profile_router

urlpatterns = [
    path("", include(profile_router.urls)),
]
