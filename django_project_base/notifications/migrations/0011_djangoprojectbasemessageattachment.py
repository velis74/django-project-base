# Generated by Django 3.2.25 on 2025-01-09 10:04

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0010_djangoprojectbasenotification_extra_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='DjangoProjectBaseMessageAttachment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='Id')),
                ('file', models.FileField(upload_to='', verbose_name='Attachment')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.djangoprojectbasemessage', verbose_name='Message')),
            ],
            options={
                'verbose_name': 'MessageAttachment',
                'abstract': False,
            },
        ),
    ]
