from django import forms
from .models import Media

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ["title", "media_type", "video_source", "file", "youtube_url", "alt_text", "caption", "is_active"]
        widgets = {
            "media_type": forms.HiddenInput(),  # hidden to pass image/video type
            "alt_text": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alt text'}),
            "caption": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Caption'}),
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        media_type = (
            self.initial.get("media_type")
            or self.instance.media_type
            or "image"
        )

        if media_type == "image":
            self.fields["file"].required = True
            self.fields["video_source"].required = False
            self.fields["youtube_url"].required = False

        elif media_type == "video":
            self.fields["video_source"].required = True
            self.fields["file"].required = False
            self.fields["youtube_url"].required = False


    def clean(self):
        cleaned_data = super().clean()

        media_type = cleaned_data.get("media_type")
        video_source = cleaned_data.get("video_source")
        file = cleaned_data.get("file")
        youtube_url = cleaned_data.get("youtube_url")

        if media_type == "video":
            if video_source == "local" and not file:
                self.add_error("file", "Please upload a video file.")

            if video_source == "youtube" and not youtube_url:
                self.add_error("youtube_url", "Please provide a YouTube URL.")

        return cleaned_data

