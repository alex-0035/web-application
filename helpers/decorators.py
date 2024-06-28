from functools import wraps

from flask import session, flash, redirect, url_for, request


def login_required(f=None, *, message="[AUTH] Please log in to access this page."):
    if f is None:
        return lambda f: login_required(f, message=message)

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(message, 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function
