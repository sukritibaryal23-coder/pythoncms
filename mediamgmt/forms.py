from django import forms
from .models import Media

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'file','alt_text','caption', 'media_type', 'is_active']
        widgets = {
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alt text'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Caption'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'media_type': forms.Select(attrs={'class': 'form-select'}),
            'homepage': forms.Select(attrs={'class': 'form-select'}),
        }
