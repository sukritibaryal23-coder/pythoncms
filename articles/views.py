from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Article
from .forms import ArticleForm
from django.db.models import F
from django.contrib import messages
from django.core.paginator import Paginator

def check_slug(request):
    slug = request.GET.get("slug", "")
    exists = Article.objects.filter(slug=slug).exists()
    return JsonResponse({"exists": exists})

def article_list(request):
    query = request.GET.get("q", "")  # get search query
    if query:
        articles = Article.objects.filter(
            title__icontains=query
        ).order_by("-id")
    else:
        articles = Article.objects.all().order_by("-id")

    paginator = Paginator(articles, 10)  # 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "articles/list.html", {
        "articles": page_obj,  # page object contains current page items
        "query": query,
        "page_obj": page_obj
    })


def article_form(request, id=None):
    article = None
    if id:
        article = get_object_or_404(Article, id=id)

    if request.method == "POST":
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                form.save()
                messages.success(request, "Article saved successfully.")
                return redirect("article_list")
            else:
                messages.error(request, "Failed to save the article.")
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/form.html", {"form": form})


def article_toggle_status(request, id):
    article = get_object_or_404(Article, id=id)
    article.status = not article.status
    article.save()
    messages.success(request, "Status Changed.")
    return redirect('article_list')

def article_homepage(request, id):
    article = get_object_or_404(Article, id=id)
    article.homepage = not article.homepage
    article.save()
    messages.success(request, "Homepage Status Changed.")
    return redirect('article_list')


def article_delete(request, id):  # <-- add "id" here
    from django.shortcuts import get_object_or_404, redirect
    from .models import Article

    article = get_object_or_404(Article, id=id)
    article.delete()
    messages.success(request, "Deleted Successfully.")
    return redirect('article_list')


def article_bulk_action(request):
    if request.method == "POST":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_articles")
        articles = Article.objects.filter(id__in=selected_ids)

        if action == "publish":
            articles.update(status=~F("status"))
            messages.success(request, "Status Changed.")
        elif action == "delete":
            articles.delete()
            messages.success(request, "Deleted Successfully.")

    return redirect('article_list')
    

