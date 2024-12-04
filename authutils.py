from functools import wraps

from braces.views import GroupRequiredMixin
from django.core.exceptions import PermissionDenied


def is_visitatore(user):
    return user.groups.filter(name='Visitatori').exists()


def is_promotore(user):
    return user.groups.filter(name='Promotori').exists()


class VisitatoreRequiredMixin(GroupRequiredMixin):
    raise_exception = True
    group_required = 'Visitatori'


class PromotoreRequiredMixin(GroupRequiredMixin):
    raise_exception = True
    group_required = 'Promotori'


def user_passes_test_403(test_func):
    """
    Decoratore per fbv che controlla la test_func passata. Se False, chiama PermissionDenied (403)
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return _wrapper_view

    return decorator


def is_visitatore(user):
    return user.groups.filter(name='Visitatori').exists()
# Create your views here.
