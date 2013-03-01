from flask.ext.wtf import Form, Required, Email, Length
from flask.ext.wtf import TextField, TextAreaField, SubmitField
from flask.ext.wtf.html5 import EmailField
from flaskext.babel import gettext as _


class ContactUsForm(Form):
    full_name = TextField(_('Full Name'), [Required()])
    email = EmailField(_('Email address'), [Required(), Email("That doesn't look like an email.")])
    subject = TextField(_('Subject'), [Required()])
    message = TextAreaField(
            label=_('Message'),
            validators=[
                Required(),
                Length(
                    max=1024,
                    ),
                ]
            )
    submit = SubmitField(_('Send Message'))
