from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.db.models import F
from .forms import UserForm

# List users
@login_required
def user_list(request):
    users = User.objects.all().order_by("-id")
    return render(request, "core/user_list.html", {"users": users})

# Add user
@login_required
def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User added successfully!")
            return redirect("core:user_list")
        else:
            messages.error(request, "Failed to add user.")
    else:
        form = UserForm()
    return render(request, "core/user_form.html", {"form": form})

# Edit user

def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect("core:user_list")
        else:
            messages.error(request, "Failed to update user.")
    else:
        form = UserForm(instance=user)
    return render(request, "core/user_form.html", {"form": form, "user": user})

# Delete user
@login_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect("core:user_list")

@login_required
def user_toggle_status(request, id):
    user = get_object_or_404(User, id=id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, "Status Changed.")
    return redirect('core:user_list')

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']  # allow GET and POST
    next_page = 'core:login'

@login_required
def user_bulk_action(request):
    if request.method == "POST":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_user")
        users = User.objects.filter(id__in=selected_ids)

        if action == "publish":
            users.update(is_active=~F("is_active"))
            messages.success(request, "Status Changed.")
        elif action == "delete":
            for user in users:
                user.delete()
            messages.success(request, "Deleted Successfully.")

    return redirect('core:user_list')