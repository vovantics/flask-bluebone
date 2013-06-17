"""This module contains the view functions for the user blueprint."""

from uuid import uuid4
from premailer import Premailer
from smtplib import SMTPDataError
from urllib import quote

from flask import (Blueprint, current_app, request, jsonify,
                   render_template)
from flask.ext.login import (login_required, current_user)
from flaskext.babel import gettext as _
from flask_mail import Message

from app.extensions import db, mail
from app.decorators import crossdomain
from app.utils import get_resource_as_string
from .models import User, UserDetail
from .forms import (ActivateForm, ChangePasswordForm,
                    DeactivateAccountForm, ProfileForm, RegisterForm,
                    RecoverPasswordForm)
from .constants import USER, ACTIVE, INACTIVE, ADMIN, STAFF
from ..session.decorators import anonymous_required


user = Blueprint('users', __name__, url_prefix='/users')

# API spec: http://labs.omniti.com/labs/jsend


@user.route('/', methods=['GET', 'OPTIONS'])
@user.route('/<int:id>/', methods=['GET', 'OPTIONS'])
@crossdomain(headers=['Content-Type'])
@login_required
def get(id=None):
    """
    Get a user given an ID.
    Get a list of users.
    """
    current_app.logger.info('Entering users.views.get()...')

    if id is None:
        if current_user.role_id == ADMIN or current_user.role_id == STAFF:
            # Get and return list of users.
            users = User.query.all()
            return jsonify(dict(users=[user.as_dict() for user in users]))
        else:
            # Get and return current user.
            response = jsonify(status='success', data=current_user.as_dict())
            response.status_code = 200
            current_app.logger.debug('Returning success; response.data=[%s]' % response.data)
            return response
    else:
        # Get the user.
        user = User.query.get(id)

        # Return the user.
        if not user:
            response = jsonify(status='fail', data={'id': 'Sorry, no user found.'})
            response.status_code = 200
            current_app.logger.debug('Returning fail; data = [Sorry, no user found.].')
            return response
        else:
            response = jsonify(status='success', data=user.as_dict())
            response.status_code = 200
            current_app.logger.debug('Returning success; response.data=[%s]' % response.data)
            return response


@user.route('/<string:email>/<string:activation_key>/', methods=['GET'])
@crossdomain()
@anonymous_required
def get_alt(email=None, activation_key=None):
    """Get a user given an email and activation key."""
    current_app.logger.info('Entering users.views.get_alt()...')

    if (email is not None and activation_key is not None):
        # Get the user.
        user = User.query.filter_by(activation_key=activation_key) \
            .filter_by(email=email).first()

        # Return the user.
        if not user:
            response = jsonify(status='fail', data={'id': 'Sorry, no user found.'})
            response.status_code = 200
            current_app.logger.debug('Returning fail; response.data=[%s]' % response.data)
            return response
        else:
            response = jsonify(status='success', data=user.as_dict())
            response.status_code = 200
            current_app.logger.debug('Returning success; response.data=[%s]' % response.data)
            return response
    else:
        response = jsonify(status='fail', data={'id': 'Sorry, no user found.'})
        response.status_code = 200
        current_app.logger.debug('Returning fail; response.data=[%s]' % response.data)
        return response


@user.route('/', methods=['POST'])
@crossdomain()
@anonymous_required
def post():
    """Create a user."""
    current_app.logger.info('Entering users.views.post()...')

    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role_id=USER,
            status_id=ACTIVE,
            user_detail=UserDetail(),
        )

        # Insert the record in our database and commit it
        db.session.add(user)
        db.session.commit()
        # Return response
        response = jsonify(status='success', data=user.as_dict())
        response.status_code = 200
        current_app.logger.debug('Returning success')
        return response
    elif request.method == 'POST':
        response = jsonify(status='fail', data=form.errors)
        response.status_code = 200
        current_app.logger.debug('Returning fail; data = [%s].' % form.errors)
        return response
    else:
        response = jsonify(status='error', message=_('Wrong data.'))
        response.status_code = 405
        current_app.logger.debug('Returning error; form errors = [%s]' % form.errors)
        return response


@user.route('/<int:id>/', methods=['DELETE'])
@crossdomain()
@login_required
def delete(id):
    """Delete a user."""
    current_app.logger.info('Entering users.views.delete()...')

    # TODO: Verify that id === current_user.id

    user = User.query.get(id)
    form = DeactivateAccountForm()
    if form.validate():
        user.status_id = INACTIVE
        db.session.add(user)
        db.session.commit()

        # Send deactivation receipt email
        css = get_resource_as_string('static/css/email.css')
        reactivate_request_url = '%s/#sessions/login/' % current_app.config['DOMAIN']
        current_app.logger.debug('reactivate_request_url=[%s]' % reactivate_request_url)
        html = render_template('user/emails/deactivate_receipt.html', css=css, username=user.username, email_recipient=user.email, reactivate_request_url=reactivate_request_url)

        p = Premailer(html)
        result_html = p.transform()

        message = Message(subject='Your %s account is now deactivated' % current_app.config['APP_NAME'], html=result_html, recipients=[user.email])
        try:
            mail.send(message)
        except SMTPDataError as e:
            current_app.logger.error('Returning fail = [%s].' % e)
            response = jsonify(status='fail', data={'email': "Couldn't send email to %s." % form.email.data})
            response.status_code = 200
            return response

        # Return response
        response = jsonify(status='success')
        response.status_code = 200
        return response
    else:
        response = jsonify(status='fail', data=form.errors)
        current_app.logger.debug('form errors = [%s]' % form.errors)
        response.status_code = 200
        return response


@user.route('/<int:id>/', methods=['PUT'])
@crossdomain()
@login_required
def put(id):
    """Update a user."""
    current_app.logger.info('Entering users.views.put()...')

    # TODO: Verify that id === current_user.id

    user = User.query.get(id)

    form = None
    if ('password' in request.data):
        form = ChangePasswordForm()
    else:
        form = ProfileForm()

    if form.validate_on_submit():
        form.populate_obj(user)
        form.populate_obj(user.user_detail)
        db.session.add(user)
        db.session.commit()

        current_app.logger.debug('Returning success.')
        response = jsonify(status='success')
        response.status_code = 200
        return response
    else:
        current_app.logger.debug('Returning fail = [%s].' % form.errors)
        response = jsonify(status='fail', data=form.errors)
        response.status_code = 200
        return response


@user.route('/password/<string:email>/<string:activation_key>/', methods=['PUT', 'OPTIONS'])
@crossdomain(headers=['Content-Type'])
@anonymous_required
def put_password(email, activation_key):
    """Update a user's password."""
    current_app.logger.info('Entering users.views.put_password()...')

    user = User.query.filter_by(activation_key=activation_key) \
                     .filter_by(email=email).first()
    form = ChangePasswordForm()

    if not user:
        response = jsonify(status='fail', data={'id': "Password couldn't be changed. Perhaps you already changed it?"})
        response.status_code = 200
        current_app.logger.debug('Returning fail; data = [Sorry, no user found.].')
        return response
    elif user and form.validate_on_submit():
        user.password = form.password.data
        if user.activation_key:
            user.activation_key = None
        db.session.add(user)
        db.session.commit()

        current_app.logger.debug('Returning success.')
        response = jsonify(status='success')
        response.status_code = 200
        return response
    else:
        current_app.logger.debug('Returning fail = [%s].' % form.errors)
        response = jsonify(status='fail', data=form.errors)
        response.status_code = 200
        return response


@user.route('/activate/<string:email>/<string:activation_key>/', methods=['PUT', 'OPTIONS'])
@crossdomain(headers=['Content-Type'])
@anonymous_required
def put_activate(email, activation_key):
    """Activate a user."""
    current_app.logger.info('Entering users.views.put_activate()...')

    user = User.query.filter_by(activation_key=activation_key) \
                     .filter_by(email=email).first()
    form = ActivateForm()

    if not user:
        response = jsonify(status='fail', data={'id': "Account couldn't be activated. Perhaps you already activated it?"})
        response.status_code = 200
        current_app.logger.debug('Returning fail; response.data=[%s]' % response.data)
        return response
    elif user and form.validate_on_submit():
        user.status_id = ACTIVE
        if user.activation_key:
            user.activation_key = None
        db.session.add(user)
        db.session.commit()

        response = jsonify(status='success')
        response.status_code = 200
        current_app.logger.debug('Returning success.')
        return response
    else:
        response = jsonify(status='fail', data=form.errors)
        response.status_code = 200
        current_app.logger.debug('Returning fail; response.data=[%s]' % response.data)
        return response


@user.route('/password/reset/', methods=['POST', 'OPTIONS'])
@crossdomain(headers=['Content-Type'])
@anonymous_required
def password_reset():
    """Request a password reset for a user."""
    form = RecoverPasswordForm()

    # TODO: Refactor this logic so the if block is not nested
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()

            # Send reset password email.
            css = get_resource_as_string('static/css/email.css')
            change_password_url = '%s/#accounts/password/reset/confirm/%s/%s/' % (current_app.config['DOMAIN'], quote(user.email), quote(user.activation_key))
            html = render_template('user/emails/reset_password.html', css=css, username=user.username, email_recipient=user.email, change_password_url=change_password_url)
            current_app.logger.debug('change_password_url=[%s]' % change_password_url)
            p = Premailer(html)
            result_html = p.transform()
            message = Message(subject='Recover your password', html=result_html, recipients=[user.email])
            try:
                mail.send(message)
            except SMTPDataError as e:
                current_app.logger.debug('Returning fail = [%s].' % e)
                response = jsonify(status='fail', data={'email': "Couldn't send email to %s." % form.email.data})
                response.status_code = 200
                return response

            current_app.logger.debug('Returning success.')
            response = jsonify(status='success')
            response.status_code = 200
            return response
        else:
            current_app.logger.debug('Returning fail = [Sorry, no user found for that email address.].')
            response = jsonify(status='fail', data={'email': 'Sorry, no user found for that email address.'})
            response.status_code = 200
            return response
    else:
        current_app.logger.debug('Returning fail = [%s].' % form.errors)
        response = jsonify(status='fail', data=form.errors)
        response.status_code = 200
        return response
