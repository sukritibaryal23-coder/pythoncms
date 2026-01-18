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
        media_type = self.instance.media_type if self.instance else kwargs.get('initial', {}).get('media_type', 'image')

        # Dynamically make fields optional depending on type
        if media_type == "image":
            self.fields['file'].required = True
            self.fields['youtube_url'].required = False
            self.fields['video_source'].required = False
        elif media_type == "video":
            self.fields['video_source'].required = True
            self.fields['file'].required = False
            self.fields['youtube_url'].required = False

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get("media_type")
        file = cleaned_data.get("file")
        video_source = cleaned_data.get("video_source")
        youtube_url = cleaned_data.get("youtube_url")

        if media_type == "image" and not file:
            raise forms.ValidationError("Image file is required!")

        if media_type == "video":
            if video_source == "youtube" and not youtube_url:
                raise forms.ValidationError("YouTube URL is required!")
            if video_source == "local" and not file:
                raise forms.ValidationError("Local video file is required!")

        return cleaned_data
