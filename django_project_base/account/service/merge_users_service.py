from typing import Optional

import django
import swapper

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models import ForeignKey
from django.utils.module_loading import import_string


class MergeUsersService:
    def handle(self, **kwargs):
        user = kwargs.get("user")
        if not user:
            return

        # TODO: handle multiple projects. In this case use signed in and has only on project available
        # if user logged in and hasnt got project selected we should run this script when project is selected
        project = swapper.load_model("django_project_base", "Project").objects.first()
        if not project:
            raise ValueError(f"Merge user service - no project found for user: {user.pk}")

        if group := self._find_group(user, project):
            try:
                with transaction.atomic():
                    self._change_user_pks(user, group)
                    if handler_function := getattr(settings, "MERGE_USERS_HANDLER", ""):
                        import_string(handler_function)(user=user, all_users=group.users, project=project)
                    group.delete()
            except Exception as e:
                import logging
                import traceback

                logger = logging.getLogger(__name__)
                logger.critical(e)
                logger.critical(str(traceback.format_exc()))

    def _find_group(self, user: "UserModel", project) -> Optional["MergeUserGroup"]:  # noqa:  F821
        MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")

        return next(
            iter(
                [
                    group
                    for group in MergeUserGroup.objects.filter(project=project)
                    if str(user.pk) in group.users.split(",")
                ]
            ),
            None,
        )

    def _change_user_pks(self, user, group):
        # TODO: this should be refactored when apps will support projects

        user_model = get_user_model()
        profile_model = swapper.load_model("django_project_base", "Profile")
        base_user_models = (user_model, profile_model, swapper.load_model("django_project_base", "MergeUserGroup"))
        users_to_merge = list(filter(lambda i: i and str(i) != str(user.pk), group.users.split(",")))
        project_model = swapper.load_model("django_project_base", "Project")

        db_tables = connection.introspection.table_names()

        for mdl in django.apps.apps.get_models(include_auto_created=True, include_swapped=True):
            if mdl not in base_user_models and not mdl._meta.abstract and not mdl._meta.swapped:
                if mdl._meta.db_table not in db_tables:
                    continue
                is_project_related = [
                    f for f in mdl._meta.fields if isinstance(f, ForeignKey) and f.related_model == project_model
                ]
                for fld in [
                    f
                    for f in mdl._meta.fields
                    if isinstance(f, ForeignKey) and (f.related_model in (user_model, profile_model))
                ]:
                    for usr in users_to_merge:
                        qs = mdl.objects.filter(**{fld.attname: fld.to_python(usr)})
                        if is_project_related:
                            p_fld = is_project_related[0]
                            qs = (
                                qs.filter(**{p_fld.attname: group.project.pk})
                                if getattr(group, "project", None)
                                else qs.filter()
                            )

                        m_items = []
                        if fld.many_to_one or fld.one_to_one:
                            m_items = mdl.objects.filter(**{fld.attname: fld.to_python(user.pk)})

                        for rec in qs:
                            try:
                                setattr(rec, fld.attname, fld.to_python(user.pk))
                                if (fld.many_to_one or fld.one_to_one) and m_items:
                                    try:
                                        rec.validate_unique()
                                        rec.save(update_fields=[fld.attname])
                                    except Exception:
                                        # record already exists, so delete record which would be duplicate
                                        rec.delete()
                                else:
                                    rec.save(update_fields=[fld.attname])
                            except Exception as e:
                                raise e
        for user in users_to_merge:
            profile = profile_model.objects.filter(pk=user_model._meta.pk.to_python(user)).first()
            if profile and profile.projects.all().count() > 1:
                # if user is on multiple projects skip deleting
                # TODO: this should be refactored when apps will support projects
                continue

            # handle all_auth tables
            if "account_emailaddress" in db_tables:
                with connection.cursor() as cursor:
                    cursor.execute("delete from public.account_emailaddress where user_id = %s", (user,))

            if "socialaccount_socialaccount" in db_tables:
                with connection.cursor() as cursor:
                    cursor.execute("truncate socialaccount_socialtoken;")
                    cursor.execute("delete from public.socialaccount_socialaccount where user_id = %s", (user,))

            profile_model.objects.filter(pk=user_model._meta.pk.to_python(user)).delete()
            user_model.objects.filter(pk=user_model._meta.pk.to_python(user)).delete()
