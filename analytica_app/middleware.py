from functools import wraps
from django.shortcuts import render
from utility.redis_utils import get_index_value, get_redis_len

def with_skeleton(template='components/skeleton_table.html'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.GET.get('load_data'):
                url = request.build_absolute_uri() + '?load_data=true'
                return render(request, template, {'custom_url': url})
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def undo_with_skeleton(template='components/skeleton_table.html'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            index_value = get_index_value(kwargs.get('id'))
            if (index_value == 0):
                return None
            elif not request.GET.get('load_data'):
                url = request.build_absolute_uri() + '?load_data=true'
                return render(request, template, {'custom_url': url})
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def redo_with_skeleton(template='components/skeleton_table.html'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            index_value = get_index_value(kwargs.get('id'))
            queue_length = get_redis_len(kwargs.get('id'))
            if (index_value == queue_length):
                return None
            elif not request.GET.get('load_data'):
                url = request.build_absolute_uri() + '?load_data=true'
                return render(request, template, {'custom_url': url})
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator