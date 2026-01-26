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

def folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    folders = Folder.objects.filter(parent=folder)
    files = MediaFile.objects.filter(folder=folder)

    return render(request, 'contentmgmt/dashboard.html', {
        'folders': folders,
        'files': files,
        'current_folder': folder,
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
    folder_id = request.POST.get('folder')
    folder = Folder.objects.filter(id=folder_id).first() if folder_id else None

    if not request.FILES:
        return JsonResponse({'success': False, 'errors': 'No files uploaded'})

    uploaded_files = []
    for f in request.FILES.getlist('file'):
        media = MediaFile.objects.create(
            file=f,
            folder=folder,
            name=f.name
        )
        uploaded_files.append({
            'id': media.id,
            'name': media.name,
            'url': media.file.url
        })

    return JsonResponse({'success': True, 'files': uploaded_files})

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

def get_folder_path(folder):
    """
    Returns a list of parent folders from root to this folder
    """
    path = []
    while folder:
        path.insert(0, folder)  # insert at the beginning
        folder = folder.parent
    return path

def folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    folders = Folder.objects.filter(parent=folder)
    files = MediaFile.objects.filter(folder=folder)

    folder_path = get_folder_path(folder)

    return render(request, 'contentmgmt/dashboard.html', {
        'folders': folders,
        'files': files,
        'current_folder': folder,
        'folder_path': folder_path,  # send path to template
    })

@require_POST
def rename_item(request):
    item_id = request.POST.get('id')
    item_type = request.POST.get('type')
    new_name = request.POST.get('name')

    if not new_name:
        return JsonResponse({'success': False})

    if item_type == 'folder':
        obj = Folder.objects.get(id=item_id)
        obj.name = new_name
        obj.save()

    elif item_type == 'file':
        obj = MediaFile.objects.get(id=item_id)
        obj.name = new_name
        obj.save()

    else:
        return JsonResponse({'success': False})

    return JsonResponse({'success': True})