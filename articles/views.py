from django.shortcuts import render, redirect, get_object_or_404
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Article
from .forms import ArticleForm
from django.db.models import F
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse

#yei ho 
from django.shortcuts import redirect

def article_home_redirect(request):
    # Only redirect if homepage param is missing
    if 'homepage' not in request.GET:
        return redirect('/articles/?homepage=1')
    # Otherwise, just render the normal list view
    from articles.views import article_list
    return article_list(request)



def check_slug(request):
    slug = request.GET.get("slug", "")
    exists = Article.all_objects.filter(slug=slug).exists()
    return JsonResponse({"exists": exists})

def article_list(request):
    # ------------------------
    # 1️⃣ Get params (with defaults)
    # ------------------------
    homepage_filter = request.GET.get("homepage", "1")  # default to homepage
    query = request.GET.get("q", "").strip()
    per_page = request.GET.get("per_page", "10")
    page_number = request.GET.get("page", 1)

    is_homepage = homepage_filter == "1"

    # ------------------------
    # 2️⃣ Base queryset
    # ------------------------
    articles = Article.objects.filter(homepage=is_homepage).order_by("position")

    # ------------------------
    # 3️⃣ Search filter
    # ------------------------
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(slug__icontains=query)
        )
#yei ho
    # ------------------------
    # 4️⃣ Pagination
    # ------------------------
    if per_page != "all":
        per_page = int(per_page)
        paginator = Paginator(articles, per_page)
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = articles  # no pagination

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'articles/_article_rows.html',  # partial template with only <tr>
            {'articles': page_obj},  # ❌ page_obj not defined yet
            request=request
        )
        return JsonResponse({'html': html})



    # ------------------------
    # 6️⃣ Normal page render
    # ------------------------
    return render(request, "articles/list.html", {
        "articles": page_obj,
        "page_obj": page_obj if per_page != "all" else None,
        "query": query,
        "per_page": per_page,
        "homepage_filter": homepage_filter,
    })

#yei ho 
def article_form(request, id=None):
    article = None
    if id:
        article = get_object_or_404(Article, id=id)

    # 🔹 READ homepage flag from URL (Add New case)
    homepage_param = request.GET.get("homepage")

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():

            saved_article = form.save(commit=False)

            # SET homepage ONLY WHEN ADDING (not editing)
            if not id and homepage_param in ["0", "1"]:
                saved_article.homepage = bool(int(homepage_param))

            if request.POST.get("delete_image") == "1":
                if article and article.image:
                    article.image.delete(save=False)
                    saved_article.image = None

            saved_article.save()

            action = request.POST.get("action")

            if action == "save":
                messages.success(request, "Article saved! You can add a new one.")
                return redirect(f"{reverse('article_add')}?homepage={homepage_param}")

            elif action == "save_more":
                messages.success(request, "Article saved! You can continue editing.")
                form = ArticleForm(instance=saved_article)
                return render(request, "articles/form.html", {"form": form})

            elif action == "save_quit":
                messages.success(request, "Article saved!")
                return redirect(f"{reverse('article_list')}?homepage={homepage_param}")

        else:
            messages.error(request, "Failed to save the article.")
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/form.html", {"form": form})



def article_toggle_status(request, id):
    if request.method == "POST":
        article = get_object_or_404(Article, id=id)
        article.status = not article.status
        article.save()

        return JsonResponse({
            "success": True,
            "status": article.status,
        })

    return JsonResponse({"success": False}, status=400)


def article_homepage(request, id):
    article = get_object_or_404(Article, id=id)
    article.homepage = not article.homepage
    article.save()
    messages.success(request, "Homepage Status Changed.")
    return redirect('article_list')


@csrf_exempt
def article_delete(request, id):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        article = get_object_or_404(Article, id=id)
        article.delete()
        return JsonResponse({
            "success": True,
            "message": "Article deleted successfully.",
        })

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


@csrf_exempt
def article_bulk_action(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_articles[]")
        articles = Article.objects.filter(id__in=selected_ids)

        if not selected_ids:
            return JsonResponse({"success": False, "message": "No articles selected."}, status=400)

        if action == "publish":
            articles.update(status=~F("status"))
            return JsonResponse({"success": True, "message": "Status updated for selected articles."})
        elif action == "delete":
            articles.delete()
            return JsonResponse({"success": True, "message": "Selected articles deleted successfully."})

        return JsonResponse({"success": False, "message": "Unsupported bulk action."}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    

@csrf_exempt
def articles_reorder(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # data['order'] is a list of article IDs
        for position, article_id in enumerate(data['order'], start=1):
            Article.objects.filter(id=article_id).update(position=position)

        return JsonResponse({"status": "ok", "message": "sorted successfully"})

    return JsonResponse({"status": "fail"}, status=400)