from functools import wraps
from django.shortcuts import render

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