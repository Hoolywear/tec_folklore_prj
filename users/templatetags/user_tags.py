from django import template

register = template.Library()


@register.filter
def is_visitatore(user):
    return user.groups.filter(name='Visitatori').exists()
