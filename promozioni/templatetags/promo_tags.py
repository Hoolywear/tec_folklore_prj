from django import template

register = template.Library()


@register.filter
def is_promotore(user):
    return user.groups.filter(name='Promotori').exists()
