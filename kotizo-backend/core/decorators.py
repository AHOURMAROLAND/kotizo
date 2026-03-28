"""Custom decorators"""
from functools import wraps

def require_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
