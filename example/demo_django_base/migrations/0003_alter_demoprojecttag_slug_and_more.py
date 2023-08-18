# Generated by Django 4.2.4 on 2023-08-18 12:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("demo_django_base", "0002_auto_20230811_1437"),
    ]

    operations = [
        migrations.AlterField(
            model_name="demoprojecttag",
            name="slug",
            field=models.SlugField(
                allow_unicode=True, max_length=100, unique=True, verbose_name="slug"
            ),
        ),
        migrations.AlterField(
            model_name="dpbtaggeditemthroughdemo",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_tagged_items",
                to="contenttypes.contenttype",
                verbose_name="content type",
            ),
        ),
        migrations.AlterField(
            model_name="dpbtaggeditemthroughdemo",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_items",
                to=settings.DJANGO_PROJECT_BASE_TAG_MODEL,
            ),
        ),
    ]
