# Generated by Django 3.1.8 on 2021-05-25 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo_django_base', '0006_auto_20210520_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='reverse_full_name_order',
            field=models.BooleanField(blank=True, null=True, verbose_name='Reverse full name order'),
        ),
    ]
