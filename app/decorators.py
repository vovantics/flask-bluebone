from datetime import timedelta
from functools import update_wrapper
from flask import current_app, request, make_response, abort


# Based on http://flask.pocoo.org/snippets/56/
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """
    origin: Optionally a list of additional URLs that might access resource.
    methods: Optionally a list of methods allowed for this view. If not
             provided it will allow all methods that are implemented.
    headers: Optionally a list of headers allowed for this request.
    max_age: The number of seconds as integer or timedelta object for which
             the preflighted request is valid.
    attach_to_all: True if decorator should add access control headers to all
                   HTTP methods or False if it should only add them to OPTIONS
                   responses.
    automatic_options: If enabled the decorator will use the default Flask
                       OPTIONS response and attach the headers there,
                       otherwise the view function will be called to generate
                       an appropriate response.
    """

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            # http://www.w3.org/TR/cors/#access-control-allow-origin-response-header
            # If origin header from client is in list of domains allowed,
            # return back to client in Access-Control-Allow-Origin header in
            # response.
            origin_allowed = None
            if request.headers.get('Origin') is None:
                abort(400)
            if origin is None and any(request.headers.get('Origin') in o for o in current_app.config['ORIGINS_ALLOWED']):
                origin_allowed = request.headers.get('Origin')
            elif origin is not None and any(request.headers.get('Origin') in o for o in (current_app.config['ORIGINS_ALLOWED'] + origin)):
                origin_allowed = request.headers.get('Origin')
            else:
                current_app.logger.warn('The remote IP [%s] requested a forbidden resource=[%s]. Returning 403.' % (request.remote_addr, request.url))
                abort(403)

            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Origin'] = origin_allowed
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
