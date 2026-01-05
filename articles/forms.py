from django import forms
from .models import Article
from django_ckeditor_5.widgets import CKEditor5Widget

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "sub_title",
            "slug",
            "content",
            "image",
            "homepage",
            "status",
            "meta_title",
            "meta_keywords",
            "meta_description",
        ]
        widgets = {
            "content": CKEditor5Widget(config_name="default")
        }
    def check_slug(request):
        slug = request.GET.get("slug", "")
        article_id = request.GET.get("id")  # get current article ID if editing

        qs = Article.objects.filter(slug=slug)
        if article_id:  # exclude the current article from check
            qs = qs.exclude(id=article_id)

        exists = qs.exists()
        return JsonResponse({"exists": exists})
        return slug
