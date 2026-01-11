from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = "core"

urlpatterns = [

    path("", RedirectView.as_view(url="users/", permanent=False)),
    path("login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="core:login"), name="logout"),
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.add_user, name="add_user"),
    path("users/edit/<int:pk>/", views.edit_user, name="edit_user"),
    path("users/delete/<int:pk>/", views.delete_user, name="delete_user"),
    path("logout/", LogoutView.as_view(next_page="core:login"), name="logout"),
    path('users/toggle-status/<int:id>/', views.user_toggle_status, name='user_toggle_status'),
     path('users/bulk-action/', views.user_bulk_action, name='user_bulk_action'),

]
