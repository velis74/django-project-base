import swapper

from django.db import transaction

from django.utils.translation import gettext_lazy as _

from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet

from django_project_base.account.middleware import ProjectNotSelectedError


class ProjectUserInviteSerializer(ModelSerializer):
    form_titles = {
        "table": "",
        "new": _("Inviting project member"),
        "edit": "",
    }

    # def confirm_create_text(self):
    #     owner_change_data = get_owner_change_data(self.context)
    #     if owner_change_data:
    #         return change_owner_warning(owner_change_data.get("free_projects_number"))
    #     return False
    #
    # def confirm_create_title(self):
    #     return _("Create project user invite confirmation")

    # def create(self, validated_data):
    # languages = validated_data.pop("languages")
    # validated_data["send_by"] = self.context["request"].user
    # invite = ProjectUserInvite.objects.create(**validated_data)
    # invite.languages.set(languages)
    #
    # # send email/generate url
    # invite_url = (
    #     ("https" if not settings.DEBUG else "http")
    #     + "://"
    #     + self.context["request"].get_host()
    #     + reverse("signup")
    #     + "%sinvitation_id=%s" % ("/?", str(invite.guid))
    # )
    # user_invite_created.send(sender=ProjectUserInvite, user_invite=invite, user_invite_url=invite_url)

    # return super().create()

    class Meta:
        model = swapper.load_model("django_project_base", "Invite")


class ProjectUserInviteViewSet(ModelViewSet):
    template_context = dict(url_reverse="project-user-invite")
    serializer_class = ProjectUserInviteSerializer

    def get_queryset(self):
        project = self.request.selected_project
        try:
            return swapper.load_model("django_project_base", "Invite").objects.filter(project_id=project)
        except ProjectNotSelectedError:
            return swapper.load_model("django_project_base", "ProjectMember").objects.none()

    # def new_object(self: viewsets.ModelViewSet):
    #     new_object = super().new_object()
    #     project_slug = self.request.query_params.get("master_project_slug")
    #     project = Project.objects.filter(slug=project_slug)
    #     if project.exists():
    #         new_object.project = project.get()
    #     return new_object

    def retrieve(self: ModelViewSet, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
