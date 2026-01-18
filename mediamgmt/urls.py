from django.urls import path
from . import views
app_name = "mediamgmt"
urlpatterns = [
    path('', views.media_list, name='media_list'),
    path("add/", views.media_form, name="media_form"),           # add media
    path("<int:id>/edit/", views.media_form, name="media_form"), # edit media
     path('<int:id>/delete/', views.media_delete, name='media_delete'),
   path("<int:id>/toggle-status/", views.media_toggle_status, name="media_toggle_status"),
    path("bulk-action/", views.media_bulk_action, name="media_bulk_action"), 
    path("reorder/", views.media_reorder, name="media_reorder"), # ← Add this
]
