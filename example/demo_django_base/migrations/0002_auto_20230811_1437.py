# Generated by Django 3.1.14 on 2023-08-11 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demo_django_base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='group',
        ),
        migrations.DeleteModel(
            name='UserGroup',
        ),
    ]
