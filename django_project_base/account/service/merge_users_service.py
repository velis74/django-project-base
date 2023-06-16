from typing import Optional

import django
import swapper
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import ForeignKey
from django.utils.module_loading import import_string


class MergeUsersService:
    def handle(self, **kwargs):
        user = kwargs.get("user")
        if not user:
            return
        if group := self._find_group(user):
            try:
                with transaction.atomic():
                    self._change_user_pks(user, group)
                    if handler_function := getattr(settings, "MERGE_USERS_HANDLER", ""):
                        import_string(handler_function)(user=user, all_users=group.users)
                    group.delete()
            except Exception as e:
                import logging

                logging.getLogger(__name__).critical(e)

    def _find_group(self, user: "UserModel") -> Optional["MergeUserGroup"]:  # noqa:  F821
        from example.demo_django_base.models import MergeUserGroup

        return next(
            iter([group for group in MergeUserGroup.objects.all() if str(user.pk) in group.users.split(",")]), None
        )

    def _change_user_pks(self, user, group):
        user_model = get_user_model()
        profile_model = swapper.load_model("django_project_base", "Profile")
        base_user_models = (user_model, profile_model)
        users_to_merge = list(filter(lambda i: i and str(i) != str(user.pk), group.users.split(",")))
        for mdl in django.apps.apps.get_models(include_auto_created=True, include_swapped=True):
            if mdl not in base_user_models and not mdl._meta.abstract and not mdl._meta.swapped:
                for fld in [
                    f for f in mdl._meta.fields if isinstance(f, ForeignKey) and (f.related_model in base_user_models)
                ]:
                    for usr in users_to_merge:
                        mdl.objects.filter(**{fld.attname: fld.to_python(usr)}).update(
                            **{fld.attname: fld.to_python(user.pk)}
                        )
        for user in users_to_merge:
            user_model.objects.filter(pk=user_model._meta.pk.to_python(user)).delete()
            profile_model.objects.filter(pk=user_model._meta.pk.to_python(user)).delete()
