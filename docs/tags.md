# Tags

Django project base supports tags usage. See example implementation below.


```python 

class DemoProjectTag(BaseTag):
   content = models.CharField(max_length=20, null=True, blank=True)
   class Meta:
       verbose_name = "Tag"
       verbose_name_plural = "Tags"

class DpbTaggedItemThroughDemo(DpbTaggedItemThrough):
    pass

class Apartment(models.Model):
    number = fields.IntegerField()
    tags = TaggableManager(through=DpbTaggedItemThroughDemo, related_name="apartment_tags")

# Example code
from example.demo_django_base.models import DemoProjectTag
dt = DemoProjectTag.objects.create(name='color tag 20', color='#ff0000')

from example.demo_django_base.models import Apartment
a = Apartment.objects.create(number=1)
a.tags.add(dt)
a.tags.all()

<QuerySet [<DemoProjectTag: color tag 20>]>

# Get background svg for tags
DemoProjectTag.get_background_svg_for_tags(Apartment.objects.all().first().tags.all())
```
