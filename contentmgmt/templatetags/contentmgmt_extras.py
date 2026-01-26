from django import template

register = template.Library()

@register.filter
def is_image(file_url):
    if not file_url:
        return False
    return file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

@register.filter
def is_video(file_url):
    if not file_url:
        return False
    return file_url.lower().endswith(('.mp4', '.webm', '.mov', '.avi'))

@register.filter
def is_pdf(file_url):
    if not file_url:
        return False
    return file_url.lower().endswith('.pdf')
