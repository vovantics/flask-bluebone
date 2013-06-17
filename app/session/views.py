# -*- coding: utf-8 -*-

from uuid import uuid4
from premailer import Premailer
from urllib import quote
from smtplib import SMTPDataError

from flask import Blueprint, current_app, jsonify, render_template, request
from flask.ext.login import login_user, current_user, logout_user, \
login_required, confirm_login
from flaskext.babel import gettext as _
from flask_mail import Message

from app.extensions import db, mail
from app.decorators import crossdomain
from app.utils import get_resource_as_string
from ..user.models import User
from .forms import LoginForm
from .decorators import anonymous_required

session = Blueprint('session', __name__, url_prefix='/session')

# API spec: http://labs.omniti.com/labs/jsend


@session.route('/', methods=['POST', 'OPTIONS'])
@crossdomain(headers='Content-Type')
@anonymous_required
def post():
    current_app.logger.info('Entering session.views.post()...')

    form = LoginForm()

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data, form.password.data)
        if user and authenticated:
            if login_user(user, remember='y'):
                response = jsonify(status='success', data=user.session_as_dict())
                response.status_code = 200
                current_app.logger.debug('Returning success; response.data=[%s]' % response.data)
                return response
            else:
                # User reactivation request.
                user.activation_key = str(uuid4())
                db.session.add(user)
                db.session.commit()

                # Send reactivation confirmation email.
                css = get_resource_as_string('static/css/email.css')
                reactivate_url = '%s/#accounts/reactivate/%s/%s/' % (current_app.config['DOMAIN'], quote(user.email), user.activation_key)
                html = render_template('user/emails/reactivate_confirm.html', css=css, username=user.username, email_recipient=user.email, reactivate_url=reactivate_url)
                current_app.logger.debug('reactivate_url=[%s]' % reactivate_url)

                p = Premailer(html)
                result_html = p.transform()

                message = Message(subject='%s Account Reactivation' % current_app.config['APP_NAME'], html=result_html, recipients=[user.email])
                try:
                    mail.send(message)
                except SMTPDataError as e:
                    current_app.logger.debug('Returning fail = [%s].' % e)
                    response = jsonify(status='fail', data={'email': "Couldn't send email to %s." % form.email.data})
                    response.status_code = 200
                    return response
                # Return response
                response = jsonify(status='success', data=user.session_as_dict())
                response.status_code = 200
                current_app.logger.debug('Returning success')
                return response
        else:
            response = jsonify(status='fail', data={'email': _('Wrong email/password.')})
            response.status_code = 200
            current_app.logger.debug('Returning success; response.data=[%s]' % response.data)
            return response
    else:
        current_app.logger.debug('Returning fail; data = [%s].' % form.errors)
        return jsonify(status='fail', data=form.errors)


@session.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(headers='Content-Type')
def get():
    current_app.logger.info('Entering session.views.get()...')


    current_app.logger.debug('SERVER_NAME=[%s]' % current_app.config['SERVER_NAME'])
    current_app.logger.debug('request.url=[%s]' % request.url)

    if current_user.is_authenticated():
        current_app.logger.debug('Returning success; response.data=[%s]' % {'auth': True, 'username': current_user.username, 'email': current_user.email, 'id': current_user.id})
        return jsonify(status='success', data=current_user.session_as_dict())
    else:
        current_app.logger.debug('Returning success; response.data=[%s]' % {'auth': False})
        return jsonify(status='success', data={'auth': False})


@session.route('/', methods=['PUT'])
@crossdomain()
@login_required
def reauth():
    current_app.logger.info('Entering session.views.reauth()...')

    # TODO: Verify current_user.email = form.data.email

    form = LoginForm()

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data, form.password.data)
        if user and authenticated:
            confirm_login()
            response = jsonify(status='success', data=user.session_as_dict())
            response.status_code = 200
            current_app.logger.debug('Returning success; response.data=[%s]' % response.data)
            return response

    current_app.logger.debug('Returning fail; data = [%s].' % form.errors)
    return jsonify(status='fail', data=form.errors)


@session.route('/', methods=['DELETE'])
@crossdomain()
@login_required
def delete():
    current_app.logger.info('Entering session.views.delete()...')
    if current_user.is_authenticated():
        logout_user()
    response = jsonify(status='success', data={'auth': False})
    response.status_code = 200
    current_app.logger.debug('Returning success')
    return response
