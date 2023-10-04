from abc import ABC, abstractmethod

import swapper
from django.shortcuts import get_object_or_404

from django_project_base.aws.ses import AwsSes
from django_project_base.constants import EMAIL_SENDER_ID_SETTING_NAME


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
            # TODO: THIS IS NOLY FOR AWS FOR NOW
            if not old_state:
                AwsSes.add_sender_email(new_state.python_value)
                return
            if old_state.python_value != new_state.python_value:
                AwsSes.remove_sender_email(old_state.python_value) if old_state.python_value else None
                AwsSes.add_sender_email(new_state.python_value)
                return


class UserRegisteredEvent(BaseEvent):
    def trigger_changed(self, old_state=None, new_state=None, payload=None, **kwargs):
        super().trigger_changed(old_state=old_state, new_state=new_state, payload=payload, **kwargs)

    def trigger(self, payload=None, **kwargs):
        super().trigger(payload, **kwargs)
        if not kwargs.get("user") or not payload or not payload.COOKIES.get("invite-pk"):
            return
        invite = get_object_or_404(swapper.load_model("django_project_base", "Invite"), pk=payload.COOKIES["invite-pk"])

        swapper.load_model("django_project_base", "ProjectMember").objects.create(
            project=invite.project, member=kwargs["user"]
        )
        from django_project_base.account.rest.project_profiles import ProjectProfilesViewSet

        setattr(payload, "selected_project", invite.project)
        ProjectProfilesViewSet().save_club_member_data(payload, kwargs["user"])
