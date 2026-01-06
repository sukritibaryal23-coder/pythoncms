from django.shortcuts import render
from articles.models import Article
from django.contrib.auth.models import User

def index(request):
    # ARTICLES
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status=True).count()
    draft_articles = Article.objects.filter(status=False).count()
    deleted_articles = Article.all_objects.filter(is_deleted=True).count()

    # USERS
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()

    # Add more app stats here if needed (comments, categories, etc.)

    context = {
        "total_articles": total_articles,
        "published_articles": published_articles,
        "draft_articles": draft_articles,
        "deleted_articles": deleted_articles,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
    }
    return render(request, "dashboard/index.html", context)
