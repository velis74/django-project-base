from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import swapper

# Create your models here.


class BaseProject(models.Model):
    name = models.CharField(max_length=80, null=False, blank=False, db_index=True)
    slug = models.SlugField(max_length=80, null=False, blank=False, db_index=True)
    description = models.TextField(null=True, blank=True)
    logo = models.FileField()
    owner = parent = models.ForeignKey(swapper.get_model_name('django_project_settings', 'Profile'))
    
    class Meta:
        abstract = True


class Project(BaseProject):
    class Meta:
        swappable = swapper.swappable_setting('django_project_settings', 'Project')


class BaseProfile(User):
    """
    User profile. We start with some easy common settings
    """
    bio = models.TextField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=20,null=True, blank=True)
    language = models.CharField(max_length=10, null=True, blank=True)  # This one will list all supported languages
    theme = models.CharField(max_length=10, null=True, blank=True)  # This one will list all supported themes
    avatar = models.FileField()

    class Meta:
        abstract = True


class Profile(BaseProfile):
    class Meta:
        swappable = swapper.swappable_setting('django_project_settings', 'Profile')


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        swapper.load_model('django_project_settings', 'Profile').objects.create(user=instance)


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
