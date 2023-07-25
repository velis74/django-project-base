import logging

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.utils import load_backend
from django.utils import timezone

from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class SendNotificationMixin(object):
    def make_send(self, notification: DjangoProjectBaseNotification, extra_data) -> DjangoProjectBaseNotification:
        sent_channels: list = []
        failed_channels: list = []
        exceptions = ""
        if notification.required_channels is None:
            return notification
        for channel_identifier in map(
            int, filter(lambda i: not (i is None), notification.required_channels.split(","))
        ):
            channel = ChannelIdentifier.channel(channel_identifier)
            try:
                channel.send(notification, extra_data)
                sent_channels.append(channel)
            except Exception as e:
                logging.getLogger(__name__).error(e)
                failed_channels.append(channel)
                exceptions += f"{str(e)}\n\n"

        if notification.pk:
            notification.sent_channels = (
                ",".join(
                    list(map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, sent_channels))))
                )
                if sent_channels
                else None
            )
            notification.failed_channels = (
                ",".join(
                    list(map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, failed_channels))))
                )
                if failed_channels
                else None
            )
            notification.sent_at = timezone.now().timestamp()
            notification.exceptions = exceptions if exceptions else None
            if db_settings := extra_data.get("DATABASE"):
                # database_backend = BaseDatabaseWrapper(db_settings)
                # database_backend.settings_dict = db_settings
                print(db_settings)
                # db_connection = connections[db_settings["ENGINE"]].get_new_connection(db_settings)

                # db_settings = connections['default'].settings_dict

                # Create a new database connection
                # db_connection = BaseDatabaseWrapper(db_settings, alias="notify")
                # db_connection.connect()

                # db_settings = connections['default'].settings_dict

                # Create a new database connection
                # db_connection = BaseDatabaseWrapper(db_settings)
                # db_connection.connect()

                # Set a custom connection alias in DATABASES settings
                # custom_db_alias = "custom_db"
                # connections.databases[custom_db_alias] = db_connection

                # db = connections.databases["default"]
                backend = load_backend(db_settings["SETTINGS"]["ENGINE"])
                db = backend.DatabaseWrapper(db_settings["SETTINGS"])
                db.connect()
                # conn = backend.DatabaseWrapper(db_settings).get_new_connection(db_settings["PARAMS"])

                # setattr(self._connections, alias, conn)

                # notification._state.db = db_wrapper.connection
                connections["defaultx"] = db.connection
                # print(db_wrapper)
                # print(db_wrapper, db_wrapper.connection)
                notification.save(
                    update_fields=["sent_at", "sent_channels", "failed_channels", "exceptions"], using="defaultx"
                )
                db.connection.close()
            else:
                notification.save(update_fields=["sent_at", "sent_channels", "failed_channels", "exceptions"])
        return notification
