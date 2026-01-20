from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import BlogForm

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
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            # Commit=False lets us modify the object before saving to DB
            blog = form.save(commit=False)
            blog.homepage = homepage 
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm(initial={'homepage': homepage})

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage
    })

def edit_blog(request, id):
    blog = get_object_or_404(Blog, id=id)  # Get the blog or 404
    session_filter = request.session.get('homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)  # Bind to existing instance
        if form.is_valid():
            blog = form.save(commit=False)
            blog.homepage = homepage  # Update homepage value if needed
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog, initial={'homepage': homepage})

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage,
        'blog': blog,  # Pass to template in case you need it
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
