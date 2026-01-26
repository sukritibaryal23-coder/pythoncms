from django.db import models
from django import template

register = template.Library()

@register.filter
def is_image(file_url):
    if not file_url:
        return False
    return file_url.lower().endswith((".jpg", ".jpeg", ".png"))

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_breadcrumbs(self):
        breadcrumbs = []
        folder = self
        while folder:
            breadcrumbs.insert(0, folder)
            folder = folder.parent
        return breadcrumbs

class MediaFile(models.Model):
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.SET_NULL, related_name='files')
    file = models.FileField(upload_to='media_files/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
