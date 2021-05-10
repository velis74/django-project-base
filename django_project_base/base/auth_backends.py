from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save

DJANGO_USER_CACHE = 'django-user-%d'


def invalidate_cache(sender, instance, **kwargs):
    if isinstance(instance, get_user_model()):
        key = DJANGO_USER_CACHE % instance.id
    else:
        key = DJANGO_USER_CACHE % instance.user_id
    cache.delete(key)


class UsersCachingBackend(ModelBackend):
    def __init__(self) -> None:
        super().__init__()
        post_save.connect(invalidate_cache, sender=get_user_model())
        post_delete.connect(invalidate_cache, sender=get_user_model())

    def get_user(self, user_id):
        user = cache.get(DJANGO_USER_CACHE % (user_id if user_id else 0))
        if not user:
            user = super().get_user(user_id)
            if user_id and user:
                cache.set(DJANGO_USER_CACHE % (user_id or 0), user)
        return user

