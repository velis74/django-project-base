from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("demo_django_base", "0008_projectinvite"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectsettings",
            name="pending_value",
            field=models.CharField(max_length=320, null=True, verbose_name="Pending value"),
        ),
        migrations.AddField(
            model_name="projectsettings",
            name="action_required",
            field=models.BooleanField(default=False, verbose_name="Action required", null=True, blank=True),
        ),
    ]
