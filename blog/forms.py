from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'subtitle','slug', 'content','homepage','active', 'meta_title', 'meta_keywords', 'meta_description']
        widgets = {
            # This keeps the field in the form but hides it from the user's eyes
            'homepage': forms.HiddenInput(),
            'slug': forms.TextInput(attrs={
                'id': 'id_slug'
            }),
            'content': forms.Textarea(attrs={'id': 'id_content'})
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance.pk:
                self.fields['slug'].widget.attrs['data-blog-id'] = self.instance.pk
