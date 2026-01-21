from django.urls import path
from . import views

app_name = 'contentmgmt'

urlpatterns = [
    path('', views.media_dashboard, name='media_dashboard'),
    path('folder/<int:folder_id>/', views.media_dashboard, name='media_dashboard_folder'),
    path('ajax/create-folder/', views.create_folder, name='create_folder'),
    path('ajax/upload-file/', views.upload_file, name='upload_file'),
    path('ajax/delete-item/', views.delete_item, name='delete_item'),
    path('ajax/toggle-status/', views.toggle_status, name='toggle_status'),
]
