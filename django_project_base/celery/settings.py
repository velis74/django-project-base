from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(length=64)
