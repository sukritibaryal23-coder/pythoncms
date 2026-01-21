from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Folder, MediaFile
from .forms import FolderForm, MediaFileForm

def media_dashboard(request, folder_id=None):
    folder = get_object_or_404(Folder, id=folder_id) if folder_id else None
    folders = Folder.objects.filter(parent=folder)
    files = MediaFile.objects.filter(folder=folder)
    breadcrumbs = folder.get_breadcrumbs() if folder else []
    return render(request, 'contentmgmt/dashboard.html', {
        'folders': folders,
        'files': files,
        'current_folder': folder,
        'breadcrumbs': breadcrumbs,
        'folder_form': FolderForm(),
        'file_form': MediaFileForm()
    })

@require_POST
def create_folder(request):
    form = FolderForm(request.POST)
    if form.is_valid():
        folder = form.save()
        return JsonResponse({'success': True, 'folder': {'id': folder.id, 'name': folder.name}})
    return JsonResponse({'success': False, 'errors': form.errors})

@require_POST
def upload_file(request):
    form = MediaFileForm(request.POST, request.FILES)
    if form.is_valid():
        media = form.save()
        return JsonResponse({'success': True, 'file': {'id': media.id, 'name': media.name, 'url': media.file.url}})
    return JsonResponse({'success': False, 'errors': form.errors})

@require_POST
def delete_item(request):
    item_type = request.POST.get('type')
    item_id = request.POST.get('id')
    if item_type == 'folder':
        Folder.objects.filter(id=item_id).delete()
    elif item_type == 'file':
        MediaFile.objects.filter(id=item_id).delete()
    return JsonResponse({'success': True})

@require_POST
def toggle_status(request):
    item_type = request.POST.get('type')
    item_id = request.POST.get('id')
    if item_type == 'folder':
        folder = get_object_or_404(Folder, id=item_id)
        folder.is_active = not folder.is_active
        folder.save()
        status = folder.is_active
    else:
        media = get_object_or_404(MediaFile, id=item_id)
        media.is_active = not media.is_active
        media.save()
        status = media.is_active
    return JsonResponse({'success': True, 'status': status})
