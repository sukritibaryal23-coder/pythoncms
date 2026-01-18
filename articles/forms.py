from django import forms
from .models import Article
from ckeditor.widgets import CKEditorWidget  # CKEditor 4 widget
# or if you use upload
from ckeditor_uploader.widgets import CKEditorUploadingWidget
import re

class ArticleForm(forms.ModelForm):
    
    class Meta:
        model = Article
        fields = [
            "title",
            "sub_title",
            "slug",
            "content",
            "image",
            "status",
            "meta_title",
            "meta_keywords",
            "meta_description",
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'required': True,
                }),
            "content": CKEditorUploadingWidget(config_name="default"),
            "image": forms.FileInput(),
            "meta_title": forms.TextInput(attrs={
                "id": "meta_title",
                "maxlength": 60     # SEO best practice
            }),
            "meta_keywords": forms.Textarea(attrs={
                "id": "meta_keywords",
                "maxlength": 250
            }),
            "meta_description": forms.Textarea(attrs={
                "id": "meta_description",
                "maxlength": 160
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "") or ""
        if content.count('class="read-more"') > 1:
            raise forms.ValidationError("Only one Read More line is allowed.")
        return content




        
    def check_slug(request):
        slug = request.GET.get("slug", "")
        article_id = request.GET.get("id")  # get current article ID if editing

        qs = Article.objects.filter(slug=slug)
        if article_id:  # exclude the current article from check
            qs = qs.exclude(id=article_id)

        exists = qs.exists()
        return JsonResponse({"exists": exists})
        return slug

    def clean_meta_keywords(self):
        data = self.cleaned_data.get("meta_keywords", "")
        if data and len(data) > 250:
            raise forms.ValidationError("Meta keywords cannot exceed 250 characters.")
        return data

    def clean_meta_description(self):
        data = self.cleaned_data.get("meta_description", "")
        if data and len(data) > 160:
            raise forms.ValidationError("Meta description cannot exceed 160 characters.")
        return data

    def clean(self):
        cleaned_data = super().clean()
        metadata_opened = self.data.get("metadata_opened") == "1"

        if metadata_opened:
            if not cleaned_data.get("meta_title"):
                self.add_error("meta_title", "Meta titles are required.")
            if not cleaned_data.get("meta_keywords"):
                self.add_error("meta_keywords", "Meta keywords are required.")
            if not cleaned_data.get("meta_description"):
                self.add_error("meta_description", "Meta description is required.")

        return cleaned_data
    


