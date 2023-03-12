from flask_login import current_user
from functools import wraps


def superuser(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(current_user.admin)
        if not current_user.admin:
            return "You are not superuser", 403
        else:
            return func(*args, **kwargs)
    return wrapper
