from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .model_registry import RECYCLE_MODELS

def recycle_bin(request):
    deleted_items = []

    for key, config in RECYCLE_MODELS.items():
        model = config["model"]
        title_field = config["title_field"]

        queryset = model.all_objects.filter(is_deleted=True)

        for obj in queryset:
            deleted_items.append({
                "id": obj.pk,
                "title": getattr(obj, title_field),
                "deleted_at": obj.deleted_at,
                "model": key,
            })

    return render(request, "recyclebin/list.html", {
        "deleted_items": deleted_items
    })

def restore(request, model, pk):
    config = RECYCLE_MODELS.get(model)
    if not config:
        return redirect("recycle_bin")

    ModelClass = config["model"]
    obj = get_object_or_404(ModelClass.all_objects, pk=pk)

    obj.restore()
    return redirect("recycle_bin")

def hard_delete(request, model, pk):
    config = RECYCLE_MODELS.get(model)
    if not config:
        return redirect("recycle_bin")

    ModelClass = config["model"]
    obj = get_object_or_404(ModelClass.all_objects, pk=pk)

    # Delete image/file if it exists
    if hasattr(obj, "image") and obj.image:
        obj.image.delete(save=False)

    obj.hard_delete()
    return redirect("recycle_bin")


