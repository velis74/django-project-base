"""demo_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django_project_base.notifications.rest.router import notifications_router
from django_project_base.profiling import app_debug_view
from django_project_base.settings import DOCUMENTATION_DIRECTORY
from django_project_base.views import documentation_view
from example.demo_django_base.views import index_view, page1_view

urlpatterns = [
    path("", index_view, name="index"),
    path("page1/", page1_view, name="page1"),
    path("dpb_admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),
    path("account/", include("django_project_base.account.urls")),
    path("", include("django_project_base.licensing.urls")),
    path("", include(notifications_router.urls)),
    path("", include("django_project_base.urls")),
    path("app-debug/", app_debug_view, name="app-debug"),
    re_path(
        r"^docs-files/(?P<path>.*)$", documentation_view, {"document_root": DOCUMENTATION_DIRECTORY}, name="docs-files"
    ),
    path("account/social/", include("social_django.urls", namespace="social")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    re_path(r"^dynamicforms/", include("dynamicforms.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
