# Generated by Django 3.1.13 on 2023-04-21 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demo_django_base', '0008_userprofile_delete_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.DJANGO_PROJECT_BASE_PROFILE_MODEL, verbose_name='Owner')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to=settings.DJANGO_PROJECT_BASE_PROJECT_MODEL, verbose_name='Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
