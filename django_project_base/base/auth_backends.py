import swapper

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save

from django_project_base.settings import USER_CACHE_KEY


def user_cache_invalidate(instance):
    if isinstance(instance, get_user_model()):
        instance_user_id = instance.id
    else:
        instance_user_id = instance.user_id

    cache.delete(USER_CACHE_KEY.format(id=instance_user_id))


def invalidate_cache(sender, instance, **kwargs):
    user_cache_invalidate(instance)


class UsersBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            user = swapper.load_model("django_project_base", "Profile").objects.get(pk=user_id)
        except Exception:
            return None
        return user if self.user_can_authenticate(user) else None


class UsersCachingBackend(UsersBackend):
    def __init__(self) -> None:
        super().__init__()
        post_save.connect(invalidate_cache, sender=get_user_model())
        post_delete.connect(invalidate_cache, sender=get_user_model())
        # even though the password is changed in Django user model, it is still UserProfile model that is saved
        #  and thus the signal for Django user model isn't firing
        post_save.connect(invalidate_cache, sender=swapper.load_model("django_project_base", "Profile"))
        post_delete.connect(invalidate_cache, sender=swapper.load_model("django_project_base", "Profile"))

    def get_user(self, user_id):
        user = cache.get(USER_CACHE_KEY.format(id=user_id or 0))
        if not user:
            user = super().get_user(user_id)
            if user_id and user:
                cache.set(USER_CACHE_KEY.format(id=user_id or 0), user)
        return user
