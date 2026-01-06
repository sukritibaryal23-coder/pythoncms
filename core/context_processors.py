from django.apps import apps
from django.urls import reverse, NoReverseMatch

def sidebar_links(request):
    links = []

    for app in apps.get_app_configs():
        # skip default Django apps
        if app.name.startswith("django."):
            continue

        # default fallback URL if 'list' view doesn't exist
        url = f"/{app.label}/"

        # try to reverse the 'list' named URL
        try:
            url = reverse(f"{app.label}:list")
        except NoReverseMatch:
            pass  # fallback to default

        links.append({
            "name": app.verbose_name.title(),
            "url": url
        })

    return {"sidebar_links": links}
