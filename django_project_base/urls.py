from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    # path('account/', include('rest_registration.api.urls')),
    path('account/', include('django_project_base.account.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
