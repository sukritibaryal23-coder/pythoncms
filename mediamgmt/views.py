from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.contrib import messages
import json

from .models import Media
from .forms import MediaForm


# ------------------------------
# 1️⃣ Media list with search/filter/pagination
# ------------------------------
def media_list(request):
    # Get filters
    media_type = request.GET.get('media_type', 'image')   # Default to 'image'
    query = request.GET.get("q", "").strip()
    per_page = request.GET.get("per_page", "10")
    page_number = request.GET.get("page", 1)

    # Base queryset: filter by media_type and not deleted
    media_qs = Media.objects.filter(media_type=media_type, is_deleted=False).order_by("sort_order")

    # Search filter
    if query:
        media_qs = media_qs.filter(Q(title__icontains=query))

    # Pagination
    if per_page != "all":
        per_page = int(per_page)
        paginator = Paginator(media_qs, per_page)
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = media_qs  # no pagination

    # AJAX live search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            "mediamgmt/media_table.html",
            {"media_list": page_obj},
            request=request
        )
        return JsonResponse({"html": html})

    # Render template
    return render(request, "mediamgmt/media_list.html", {
        "media_list": page_obj,
        "page_obj": page_obj if per_page != "all" else None,
        "query": query,
        "per_page": per_page,
        "media_type": media_type,
    })

def media_video_form(request, id=None):
    """
    Handles both adding new video media and editing existing video media.
    """
    media = None
    if id:
        media = get_object_or_404(
            Media,
            id=id,
            is_deleted=False,
            media_type="video"
        )

    media_type = "video"  # force video

    if request.method == "POST":
        form = MediaForm(request.POST, request.FILES, instance=media)
        if form.is_valid():
            saved_media = form.save(commit=False)

            # If user requested to delete current file
            if request.POST.get("delete_file") == "1":
                if media and media.file:
                    media.file.delete(save=False)
                    saved_media.file = None

            # Always set media type to video
            saved_media.media_type = media_type

            saved_media.save()

            action = request.POST.get("action")

            if action == "save":
                messages.success(request, "Video saved! You can add a new one.")
                return redirect(reverse("mediamgmt:media_video_form"))

            elif action == "save_more":
                messages.success(request, "Video saved! You can continue editing.")
                form = MediaForm(instance=saved_media)
                return render(
                    request,
                    "mediamgmt/media_video_form.html",
                    {
                        "form": form,
                        "media": saved_media,
                        "media_type": media_type,
                    },
                )

            elif action == "save_quit":
                messages.success(request, "Video saved!")
                return redirect(f"{reverse('mediamgmt:media_list')}?media_type=video")

        else:
            messages.error(request, "Failed to save video. See errors below.")
            print(form.errors)

    else:
        form = MediaForm(instance=media)

    return render(
        request,
        "mediamgmt/media_video_form.html",
        {
            "form": form,
            "media": media,
            "media_type": media_type,
        },
    )


# ------------------------------
# 2️⃣ Media add/edit
# ------------------------------
def media_form(request, id=None):
    """
    Handles both adding new media (id=None) and editing existing media (id provided).
    """
    media = None
    if id:
        media = get_object_or_404(Media, id=id, is_deleted=False)

    # Get media_type from query params if adding new
    media_type = request.GET.get('media_type', 'image') if not media else media.media_type

    if request.method == "POST":
        form = MediaForm(request.POST, request.FILES, instance=media)
        if form.is_valid():
            saved_media = form.save(commit=False)

            # If user requested to delete current file
            if request.POST.get("delete_file") == "1":
                if media and media.file:
                    media.file.delete(save=False)
                    saved_media.file = None

            # Set media type when adding new
            if not media:
                saved_media.media_type = media_type

            saved_media.save()

            action = request.POST.get("action")

            if action == "save":  # Save & go to add new
                messages.success(request, "Media saved! You can add a new one.")
                return redirect(f"{reverse('mediamgmt:media_form')}?media_type={media_type}")

            elif action == "save_more":  # Save & stay on same media
                messages.success(request, "Media saved! You can continue editing.")
                form = MediaForm(instance=saved_media)
                return render(
                    request, "mediamgmt/media_form.html", {"form": form, "media": saved_media, "media_type": media_type}
                )

            elif action == "save_quit":  # Save & go back to list
                messages.success(request, "Media saved!")
                return redirect(f"{reverse('mediamgmt:media_list')}?media_type={media_type}")

        else:
            # Form invalid: show errors
            messages.error(request, "Failed to save media. See errors below.")
            print(form.errors)  # Optional: log errors for debugging
    else:
        # GET request
        form = MediaForm(instance=media)

    return render(
        request,
        "mediamgmt/media_form.html",
        {"form": form, "media": media, "media_type": media_type},
    )
# ------------------------------
# 3️⃣ Toggle status
# ------------------------------
def media_toggle_status(request, id):
    if request.method == "POST":
        try:
            media = Media.objects.get(id=id)
            media.is_active = not media.is_active
            media.save()
            return JsonResponse({"success": True, "is_active": media.is_active})
        except Media.DoesNotExist:
            return JsonResponse({"success": False, "error": "Media not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})


# ------------------------------
# 4️⃣ Soft delete
# ------------------------------
@csrf_exempt
def media_delete(request, id):
    # Ensure only AJAX POST requests are allowed
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        # Get media object that is not already deleted
        media = get_object_or_404(Media, id=id, is_deleted=False)
        
        # Perform soft delete
        media.is_deleted = True  # your SoftDeleteModel probably has this field
        media.save()
        
        return JsonResponse({
            "success": True,
            "message": "Media moved to recycle bin successfully.",
        })
    
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

# ------------------------------
# 5️⃣ Bulk actions
# ------------------------------
@csrf_exempt
def media_bulk_action(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_media[]")
        media_qs = Media.objects.filter(id__in=selected_ids, is_deleted=False)

        if not selected_ids:
            return JsonResponse({"success": False, "message": "No media selected."}, status=400)

        if action == "publish":
            media_qs.update(is_active=~F("is_active"))
            return JsonResponse({"success": True, "message": "Status updated for selected media."})
        elif action == "delete":
            media_qs.delete()  # soft delete
            return JsonResponse({"success": True, "message": "Selected media deleted successfully."})

        return JsonResponse({"success": False, "message": "Unsupported bulk action."}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


# ------------------------------
# 6️⃣ Reorder media
# ------------------------------
@csrf_exempt
def media_reorder(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order = data.get("order", [])

            for index, media_id in enumerate(order):
                Media.objects.filter(id=media_id).update(sort_order=index)

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request method"})