from django.db import models
from core.models import SoftDeleteModel  # your existing SoftDeleteModel

class Media(SoftDeleteModel):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    VIDEO_SOURCES = (
        ('local', 'Local Video'),
        ('youtube', 'YouTube'),
    )

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="media/", blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    youtube_url = models.URLField(blank=True, null=True)  # NEW
    video_source = models.CharField(
        max_length=10,
        choices=VIDEO_SOURCES,
        default='local'
    )  # NEW
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)  # for drag-and-drop
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title
