import itertools
from django.db import models
from core.models import SoftDeleteModel
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
import re
# Create your models here.


class Article(SoftDeleteModel):
    title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = RichTextUploadingField()
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    homepage = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_keywords = models.CharField(max_length=250, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from title
            self.slug = slugify(self.title)
            
        super().save(*args, **kwargs)
    def __str__(self):
        return str(self.title or "")
    
    class Meta:
        ordering = ['position']
