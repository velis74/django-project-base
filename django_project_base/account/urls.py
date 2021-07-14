from django.urls import include, path

from .router import accounts_router

urlpatterns = [
    path('', include(accounts_router.urls)),
]
