from django.contrib import admin
from django.db import models

from django_project_base.models import BaseProfile, BaseProject


class UserProfile(BaseProfile):
    pass


class Project(BaseProject):
    owner = models.ForeignKey(UserProfile, related_name='user_profiles', on_delete=models.CASCADE)


admin.site.register(Project)
