# Generated by Django 4.2.4 on 2023-08-29 07:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("licensing", "0003_alter_licenseaccessuse_comment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="licenseaccessuse",
            name="amount",
            field=models.FloatField(default=0),
        ),
    ]