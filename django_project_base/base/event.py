import copy
import datetime
from abc import ABC, abstractmethod

import swapper
from django.conf import settings
from django.shortcuts import get_object_or_404

from django_project_base.constants import EMAIL_SENDER_ID_SETTING_NAME, SMS_SENDER_ID_SETTING_NAME


class UserModel:
    pk: int


class BaseEvent(ABC):
    user: UserModel

    def __init__(self, user: UserModel) -> None:
        super().__init__()
        self.user = user

    @abstractmethod
    def trigger(self, payload=None, **kwargs):
        pass

    @abstractmethod
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        self.trigger(payload=payload, **kwargs)


class ProjectSettingChangedEvent(BaseEvent):
    def trigger(self, payload=None, **kwargs):
        super().trigger(payload=payload, **kwargs)

    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)


class EmailSenderChangedEvent(ProjectSettingChangedEvent):
    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)

    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state, new_state, payload, **kwargs)

        if new_state.name == EMAIL_SENDER_ID_SETTING_NAME:
            # TODO: THIS IS ONLY FOR AWS FOR NOW
            # from django_project_base.aws.ses import AwsSes

            if not old_state:
                print("AWS add EMAIL")
                return
                # AwsSes.add_sender_email(new_state.python_value)
                # return
            if (old_state.python_value != new_state.python_value) or (
                new_state.python_value
                and new_state.pending_value
                and new_state.python_pending_value != new_state.python_value
            ):
                return

                print("AWS SEND EMAIL")
                # AwsSes.add_sender_email(new_state.pending_value)
                # return
            # clear old email - or not what if another project is using email ???
            # go through all project and delete diff AMAZON - DB
            # ####### AwsSes.remove_sender_email(old_state.python_value) if old_state.python_value else None


class SmsSenderChangedEvent(ProjectSettingChangedEvent):
    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)

    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state, new_state, payload, **kwargs)

        if new_state.name == SMS_SENDER_ID_SETTING_NAME:
            pass


class UserInviteFoundEvent(BaseEvent):
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)

    def trigger(self, payload=None, **kwargs):
        super().trigger(payload=payload)
        if not payload or payload.accepted or not kwargs.get("request"):
            return

        swapper.load_model("django_project_base", "ProjectMember").objects.get_or_create(
            project=payload.project, member=self.user.userprofile
        )
        from django_project_base.account.rest.project_profiles import ProjectProfilesViewSet

        setattr(kwargs["request"], "selected_project", payload.project)
        ProjectProfilesViewSet().save_club_member_data(kwargs["request"], self.user.userprofile)
        payload.accepted = datetime.datetime.now()
        payload.save(update_fields=["accepted"])

        if current_project_attr := (
            getattr(settings, "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES", {})
            .get("project", {})
            .get("value_name", None)
        ):
            kwargs["request"].session[current_project_attr] = payload.project.slug
        kwargs["request"].session.pop("invite-pk", None)


class UserRegisteredEvent(BaseEvent):
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)

    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)
        if not payload:
            return

        if invite_pk := payload.session.get("invite-pk"):
            invite = get_object_or_404(swapper.load_model("django_project_base", "Invite"), pk=invite_pk)
            UserInviteFoundEvent(self.user).trigger(payload=invite, request=payload)
            return
        payload.session.pop("invite-pk", None)


class UserLoginEvent(BaseEvent):
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)

    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)
        if not payload:
            return

        if invite_pk := payload.session.get("invite-pk"):
            invite = get_object_or_404(swapper.load_model("django_project_base", "Invite"), pk=invite_pk)
            UserInviteFoundEvent(self.user).trigger(payload=invite, request=payload)
            return
        payload.session.pop("invite-pk", None)


class ProjectSettingConfirmedEvent(BaseEvent):
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)

    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)
        if not payload:
            return
        from django_project_base.aws.ses import AwsSes

        def confirm(item):
            item.value = copy.copy(item.python_pending_value)
            item.pending_value = None
            item.save(update_fields=["value", "pending_value"])

        # not self.user Event is trigerred from management command
        if payload.name == EMAIL_SENDER_ID_SETTING_NAME and (
            payload.python_pending_value in AwsSes.list_verified_sender_emails() or not self.user
        ):
            confirm(payload)
        if payload.name == SMS_SENDER_ID_SETTING_NAME:
            if not self.user:
                confirm(payload)


class ProjectSettingPendingResetEvent(BaseEvent):
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)

    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)
        if not payload:
            return
        from django_project_base.aws.ses import AwsSes

        payload.pending_value = None
        payload.save(update_fields=["value", "pending_value"])

        if payload.name == EMAIL_SENDER_ID_SETTING_NAME:
            if payload.python_pending_value in AwsSes.list_sender_emails():
                AwsSes.remove_sender_email(payload.python_pending_value)
        if payload.name == SMS_SENDER_ID_SETTING_NAME:
            pass
