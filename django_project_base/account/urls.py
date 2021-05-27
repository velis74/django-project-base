from django.urls import include, path

from .router import router

urlpatterns = [
    path('', include(router.urls)),
    path('social/', include('social_django.urls', namespace="social")),
]
