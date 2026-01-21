from django import template

register = template.Library()

@register.filter
def is_image(value):
    """Returns True if the file URL ends with common image extensions"""
    if not value:
        return False
    value = value.lower()
    return value.endswith('.jpg') or value.endswith('.jpeg') or value.endswith('.png')
