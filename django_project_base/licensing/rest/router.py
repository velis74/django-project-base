from rest_framework.routers import DefaultRouter

from django_project_base.licensing.rest.rest import LicenseViewSet

licensing_router = DefaultRouter()

licensing_router.register(
    r"license",
    LicenseViewSet,
    basename="license",
)
