from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import BlogForm
from django.db.models import F
from django.contrib import messages
from django.urls import reverse

def blog_list(request):
    # 1. Capture the parameter if it exists in the URL
    homepage_param = request.GET.get('homepage')
    
    if homepage_param is not None:
        # Save the choice to the session
        request.session['homepage_filter'] = homepage_param
        # Redirect to the 'clean' URL (removes ?homepage=X from address bar)
        return redirect('blog_list')

    # 2. Get the value from session, default to '1' (Inner Page) if session is empty
    current_filter = request.session.get('homepage_filter', '0')

    # Filtering
    blog = Blog.objects.filter(homepage=current_filter).order_by('position')

    return render(request, 'blog/list.html', {
        'list': blog, 
        'current_filter': current_filter
    })


def create_blog(request):
    session_filter = request.session.get('homepage_filter', '0')
    homepage = session_filter == '1'
    homepage_param = '1' if homepage else '0'

    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.homepage = homepage
            blog.save()

            action = request.POST.get("action")

            if action == "save":
                messages.success(request, "Blog saved! You can add a new one.")
                return redirect(f"{reverse('create_blog')}?homepage={homepage_param}")

            elif action == "save_more":
                messages.success(request, "Blog saved! You can continue editing.")
                return redirect('blog_edit', id=blog.id)

            elif action == "save_quit":
                messages.success(request, "Blog saved!")
                return redirect(f"{reverse('blog_list')}?homepage={homepage_param}")

    else:
        form = BlogForm()

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage,
    })
def edit_blog(request, id):
    blog = get_object_or_404(Blog, id=id)

    session_filter = request.session.get('homepage_filter', '0')
    homepage = session_filter == '1'
    homepage_param = '1' if homepage else '0'

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.homepage = homepage
            blog.save()

            action = request.POST.get("action")

            if action == "save_more":
                messages.success(request, "Changes saved.")
                return redirect('blog_edit', id=blog.id)

            elif action == "save_quit":
                messages.success(request, "Changes saved.")
                return redirect(f"{reverse('blog_list')}?homepage={homepage_param}")

    else:
        form = BlogForm(instance=blog)

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage,
        'blog': blog,
    })

def sort(request, module):
    data = json.loads(request.body)
    order = data.get('order', [])

    for index, item_id in enumerate(order):
        # Adjust model name if needed
        Blog.objects.filter(id=item_id).update(position=index)

    return JsonResponse({'status': 'ok'})

def blog_delete(request, id):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        blog = get_object_or_404(Blog, id=id)
        # --- Soft delete ---
        if hasattr(blog, "is_deleted"):
            blog.is_deleted = True
            blog.save()
            return JsonResponse({
            "success": True,
            "message": "Article deleted successfully.",
        })
        else:
            # Hard delete if no is_deleted field
            blog.delete()
            return JsonResponse({
            "success": True,
            "message": "Article deleted successfully.",
        })

        return JsonResponse({
            "success": True,
            "message": "Blog deleted successfully."
        })

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

def blog_toggle_status(request, id):
    if request.method == "POST":
        blog = get_object_or_404(Blog, id=id)
        blog.active = not blog.active
        blog.save()

        return JsonResponse({
            "success": True,
            "active": blog.active,
        })

    return JsonResponse({"success": False}, status=400)

def blog_bulk_action(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_blogs[]")  # Make sure your frontend uses this name
        blogs = Blog.objects.filter(id__in=selected_ids)

        if not selected_ids:
            return JsonResponse({"success": False, "message": "No blogs selected."}, status=400)

        if action == "publish":
            # Toggle status for each selected blog
            for blog in blogs:
                blog.active = not blog.active
                blog.save()
            return JsonResponse({"success": True, "message": "Status updated for selected blogs."})

        elif action == "delete":
            blogs.delete()
            return JsonResponse({"success": True, "message": "Selected blogs deleted successfully."})

        return JsonResponse({"success": False, "message": "Unsupported bulk action."}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    