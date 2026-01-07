from django.shortcuts import render, get_object_or_404, redirect
from articles.models import Article

def recycle_bin(request):
    deleted_articles = Article.all_objects.filter(is_deleted=True)
    return render(request, "recyclebin/list.html", {"deleted_articles": deleted_articles})

def restore(request, model, pk):
    model_map = {
        "article": Article,
    }
    obj = get_object_or_404(model_map[model].all_objects, pk=pk)
    obj.restore()
    return redirect("recycle_bin")

def hard_delete(request, model, pk):
    model_map = {
        "article": Article,
    }
    
    obj = get_object_or_404(model_map[model].all_objects, pk=pk)

    # Delete the image file if it exists
    if obj.image:  # check instance's image
        obj.image.delete(save=False)  # delete the file from storage

    # Hard delete the object from database
    obj.hard_delete()
    
    return redirect("recycle_bin")

