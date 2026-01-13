from flask_login import current_user
from flask import abort
from functools import wraps

def permission_required(code):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_permission(code):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
