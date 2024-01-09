from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(length=64)

# todo: read this setting from env
NOTIFICATION_SEND_PAUSE_SECONDS = 1

# todo: read this setting from env
NOTIFICATION_QUEABLE_HARD_TIME_LIMIT = 180

# todo: read this setting from env
NOTIFICATIONS_QUEUE_VISIBILITY_TIMEOUT = 86400
