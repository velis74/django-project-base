# Generated by Django 4.2.4 on 2023-08-31 10:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_remove_djangoprojectbasenotification_project_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="djangoprojectbasemessage",
            options={"verbose_name": "Notification Message"},
        ),
        migrations.AlterModelOptions(
            name="djangoprojectbasenotification",
            options={"verbose_name": "Notification"},
        ),
    ]
