# Generated by Django 3.2.23 on 2024-01-10 15:03

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('demo_django_base', '0010_alter_projectsettings_action_required_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', related_name='apartment_tags', through='demo_django_base.DpbTaggedItemThroughDemo', to='demo_django_base.DemoProjectTag', verbose_name='Tags'),
        ),
    ]
