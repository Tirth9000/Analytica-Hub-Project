from django import template

register = template.Library()

@register.filter
def key(dictionary, key_name):
    return dictionary.get(key_name, None)