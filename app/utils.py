from functools import wraps
from flask import jsonify, redirect, url_for
from flask_login import current_user


def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_superuser", False):
            return jsonify(
                {"error": "Unauthorized. Superuser access required."}), 403

        return f(*args, **kwargs)

    return decorated_function
