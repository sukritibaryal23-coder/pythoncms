from django import forms
from .models import Folder, MediaFile

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file', 'folder']
