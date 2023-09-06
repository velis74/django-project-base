# Generated by Django 4.2.4 on 2023-09-05 08:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from django_project_base.constants import (
    EMAIL_SENDER_ID_SETTING_NAME,
    SMS_SENDER_ID_SETTING_NAME,
    NOTIFY_NEW_USER_SETTING_NAME,
)


def forwards_func(apps, schema_editor):
    ProjectModel = apps.get_model("demo_django_base", "Project")
    ProjectModelSettings = apps.get_model("demo_django_base", "ProjectSettings")
    for project in ProjectModel.objects.all():
        email_sender = project.email_sender_id
        sms_sender = project.sms_sender_id

        ProjectModelSettings.objects.create(
            name=EMAIL_SENDER_ID_SETTING_NAME,
            project=project,
            description="From email address for notifications",
            value=email_sender or "",
            value_type="char",
        )

        ProjectModelSettings.objects.create(
            project=project,
            name=SMS_SENDER_ID_SETTING_NAME,
            description="Sms sender name for notifications",
            value=sms_sender or "",
            value_type="char",
        )

        ProjectModelSettings.objects.create(
            project=project,
            name=NOTIFY_NEW_USER_SETTING_NAME,
            description="Notify new user account was created for him",
            value=True,
            value_type="bool",
        )


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        (
            "demo_django_base",
            "0004_alter_demoprojecttag_name_alter_demoprojecttag_slug_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(db_index=True, max_length=80, verbose_name="Name"),
                ),
                (
                    "description",
                    models.CharField(max_length=120, verbose_name="Description"),
                ),
                ("value", models.CharField(max_length=320, verbose_name="Value")),
                (
                    "value_type",
                    models.CharField(
                        choices=[
                            ("integer", "Whole number"),
                            ("float", "Decimal number"),
                            ("bool", "true/false"),
                            ("char", "String"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.DJANGO_PROJECT_BASE_PROJECT_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.RemoveField(
            model_name="project",
            name="email_sender_id",
        ),
        migrations.RemoveField(
            model_name="project",
            name="sms_sender_id",
        ),
        migrations.AlterUniqueTogether(
            name="projectsettings",
            unique_together={("project", "name")},
        ),
    ]
