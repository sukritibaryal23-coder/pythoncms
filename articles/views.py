from django.shortcuts import render, redirect, get_object_or_404
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Article
from .forms import ArticleForm
from django.db.models import F
from django.contrib import messages
from django.core.paginator import Paginator


def check_slug(request):
    slug = request.GET.get("slug", "")
    exists = Article.all_objects.filter(slug=slug).exists()
    return JsonResponse({"exists": exists})



from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Article

def article_list(request):
    query = request.GET.get("q", "")
    per_page = request.GET.get("per_page", "10")
    homepage_filter = request.GET.get("homepage", "")  # NEW: homepage filter

    # BASE QUERYSET
    articles = Article.objects.all()
    
    # SEARCH FILTER
    if query:
        articles = articles.filter(title__icontains=query)

    # HOMEPAGE FILTER
    if homepage_filter in ["0", "1"]:
        articles = articles.filter(homepage=bool(int(homepage_filter)))

    # DRAG & DROP ORDER
    articles = articles.order_by("position")

    # =========================
    # AJAX LIVE SEARCH RESPONSE
    # =========================
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if per_page != "all":
            per_page = int(per_page)
            paginator = Paginator(articles, per_page)
            page_number = request.GET.get("page")
            articles = paginator.get_page(page_number)

        html = render_to_string(
            "articles/_article_rows.html",
            {"articles": articles},
            request=request
        )
        return JsonResponse({"html": html})

    # =========================
    # NORMAL PAGE LOAD
    # =========================
    if per_page == "all":
        page_obj = articles
    else:
        per_page = int(per_page)
        paginator = Paginator(articles, per_page)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

    return render(request, "articles/list.html", {
        "articles": page_obj,
        "page_obj": page_obj if per_page != "all" else None,
        "query": query,
        "per_page": per_page,
        "homepage_filter": homepage_filter,  # send to template for dropdown pre-selection
    })




def article_form(request, id=None):
    article = None
    if id:
        article = get_object_or_404(Article, id=id)

    if request.method == "POST":
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                
                if request.POST.get("delete_image") == "1":
                    if article and article.image:
                        article.image.delete(save=False)
                        article.image = None
                saved_article = form.save()
                action = request.POST.get("action")

                if action == "save":
                    messages.success(request, "Article saved! You can add a new one.")
                    return redirect('article_add')

                elif action == "save_more":
                    messages.success(request, "Article saved! You can continue editing.")
                    # Render the same page with the saved article instance
                    form = ArticleForm(instance=saved_article)  # Ensure form is pre-filled
                    return render(request, "articles/form.html", {"form": form})

                elif action == "save_quit":
                    messages.success(request, "Article saved!")
                    return redirect('article_list')

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
            for article in articles:
                article.delete()
            messages.success(request, "Deleted Successfully.")

    return redirect('article_list')
    

@csrf_exempt
def articles_reorder(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # data['order'] is a list of article IDs
        for position, article_id in enumerate(data['order'], start=1):
            Article.objects.filter(id=article_id).update(position=position)

        return JsonResponse({"status": "ok", "message": "sorted successfully"})

    return JsonResponse({"status": "fail"}, status=400)