"""
decorators.py

Decorators for URL handlers

"""

from functools import wraps
from flask import redirect, request, abort
import flask_login


def login_required(func):
    """Requires standard login credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = flask_login.current_user
        if not user.is_authenticated():
            abort(401)
        return func(*args, **kwargs)
    return decorated_view


def admin_required(func):
    """Requires App Engine admin credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = flask_login.current_user
        if user.is_authenticated():
            if user.role != 'ADMIN':
                abort(401)  # Unauthorized
            return func(*args, **kwargs)
        else:
            abort(401)
    return decorated_view
