from django.db import models
from core.models import SoftDeleteModel
from django.utils.text import slugify

# Create your models here.
class Blog(SoftDeleteModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    homepage = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False) 
    meta_title = models.CharField(max_length=200, blank=True)
    meta_keywords = models.CharField(max_length=250, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    class Meta:
        ordering = ['position']

def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)