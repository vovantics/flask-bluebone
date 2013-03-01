from functools import wraps
from flask import redirect, url_for
from flask.ext.login import current_user


# TODO: remove Redirect if user already logged in
#    if current_user is not Anonymous and current_user.is_authenticated():
#        return redirect(url_for('home'))
def anonymous_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated():
            return redirect(url_for('meta.index'))
        return f(*args, **kwargs)
    return decorated
