from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class LicenseAccessUse(models.Model):
    USE = 4
    ADMIN_USE = 10

    CHOICES = ((USE, _("Used access")), (ADMIN_USE, _("Used access by admin")))
    date = models.DateTimeField(
        verbose_name=_("Date"), default=now, null=False, blank=False
    )
    type = models.IntegerField(verbose_name=_("Type"), choices=CHOICES, default=USE)

    user_id = models.CharField(max_length=1024, db_index=True)

    content_type_object_id = models.CharField(max_length=1024)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)

    comment = models.CharField(
        max_length=255, verbose_name=_("Comment"), null=True, blank=False
    )
