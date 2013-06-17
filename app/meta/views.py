"""This module contains the view functions for the meta blueprint."""
from premailer import Premailer

from flask import (Blueprint, render_template, current_app, flash, \
    jsonify)
from flask_mail import Message
from flaskext.babel import gettext as _
from app.utils import get_resource_as_string, get_current_time
from app.extensions import mail
from .forms import ContactUsForm

meta = Blueprint('meta', __name__)


@meta.route('/')
def index():
    True


@meta.route('/mail/', methods=['POST'])
def contact():
    """Send an email to the ADMINS."""
    current_app.logger.info('Entering meta.views.contact()...')

    form = ContactUsForm()

    if form.validate_on_submit():
        subject = '[%s] Message from %s: %s' % (current_app.config['APP_NAME'], form.full_name.data, form.subject.data)
        date = get_current_time()

        css = get_resource_as_string('static/css/email.css')
        html = render_template('meta/emails/contact.html', css=css, email_recipient=form.email.data, full_name=form.full_name.data, date=date, title=subject, message=form.message.data)

        p = Premailer(html)
        result_html = p.transform()

        message = Message(subject=subject, html=result_html, reply_to=form.email.data, recipients=current_app.config['ADMINS'])
        mail.send(message)

        flash(_("Thanks for your message. We'll get back to you shortly."), 'success')

    current_app.logger.debug('Returning success.')
    response = jsonify(status='success')
    response.status_code = 200
    return response
