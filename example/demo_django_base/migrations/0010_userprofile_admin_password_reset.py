# Generated by Django 3.1 on 2023-06-01 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo_django_base', '0009_projectmember'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='password_invalid',
            field=models.BooleanField(default=False),
        ),
    ]