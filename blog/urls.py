from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('create/', views.create_blog, name='create_blog'),
    path('edit/<int:id>/', views.edit_blog, name='blog_edit'),
    path('sort/<str:module>/', views.sort, name='sort'),  # ✅ ADD THIS
    path('delete/<int:id>/', views.blog_delete, name='blog_delete'),
    path('toggle-status/<int:id>/', views.blog_toggle_status, name='blog_toggle_status'),
    path('bulk-action/', views.blog_bulk_action, name='blog_bulk_action'),


]