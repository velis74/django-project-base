from django.urls import include, path

from .router import accounts_router

urlpatterns = [
    path('', include(accounts_router.urls)),
    path('social/', include('social_django.urls', namespace="social")),
]
