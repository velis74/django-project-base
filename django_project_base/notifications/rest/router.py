from rest_framework.routers import DefaultRouter

from django_project_base.notifications.rest.delivery_report import DeliveryReportViewSet
from django_project_base.notifications.rest.maintenance_notification import UsersMaintenanceNotificationViewset
from django_project_base.notifications.rest.notification import (
    NotificationDelayViewSet,
    NotificationsLicenseViewSet,
    NotificationViewset,
)


class NotificationsRouter(DefaultRouter):
    pass


notifications_router: NotificationsRouter = DefaultRouter()

notifications_router.register(
    r"maintenance-notification", UsersMaintenanceNotificationViewset, basename="maintenance-notification"
)
notifications_router.register(r"notification", NotificationViewset, basename="notification")
notifications_router.register(r"notification-delay", NotificationDelayViewSet, basename="notification-delay")
notifications_router.register(r"notification-license", NotificationsLicenseViewSet, basename="notification-license")
notifications_router.register(
    r"notification-dlr",
    DeliveryReportViewSet,
    basename="notification-dlr",
)
