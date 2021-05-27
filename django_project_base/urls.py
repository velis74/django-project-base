from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from django_project_base.router import django_project_base_urlpatterns

urlpatterns = [
    path('account/', include('rest_registration.api.urls')),
    path('account/', include('django_project_base.account.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
] + django_project_base_urlpatterns
