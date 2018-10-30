from django import template

register = template.Library()

@register.simple_tag
def nested_get(dct, item1, item2):
    return dct.get(item1, {}).get(item2, '')
