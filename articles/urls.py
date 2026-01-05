from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('add/', views.article_form, name='article_add'),
    path('edit/<int:id>/', views.article_form, name='article_edit'),
    path('bulk-action/', views.article_bulk_action, name='article_bulk_action'),


    # Delete article
    path('delete/<int:id>/', views.article_delete, name='article_delete'),

    # Toggle publish/unpublish
    path('toggle-status/<int:id>/', views.article_toggle_status, name='article_toggle_status'),

    path("check-slug/", views.check_slug, name="check_slug"),
]
