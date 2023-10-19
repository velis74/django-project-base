from django.urls import include, path

from django_project_base.account.router import accounts_router, profile_router

urlpatterns = [
    path("", include(accounts_router.urls)),
    path("", include(profile_router.urls)),
]
