from django.urls import path
from . import views

urlpatterns = [
    path("", views.recycle_bin, name="recycle_bin"),
    path("restore/<str:model>/<int:pk>/", views.restore, name="recycle_restore"),
    path("hard-delete/<str:model>/<int:pk>/", views.hard_delete, name="recycle_hard_delete"),
]
