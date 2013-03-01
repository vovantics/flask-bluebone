from flask.ext.wtf import Form, Required, Email, Length
from flask.ext.wtf import PasswordField, SubmitField
from flask.ext.wtf.html5 import EmailField
from flaskext.babel import gettext as _
from ..user.constants import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)


class LoginForm(Form):
    email = EmailField(
        label=_('Email address'),
        validators=[
            Email(message=_("That doesn't look like an email."))
            ]
        )
    password = PasswordField(
        label=_('Password'),
        validators=[
            Required(),
            Length(
                min=PASSWORD_LEN_MIN,
                max=PASSWORD_LEN_MAX,
                )
            ]
        )
    #remember_me = BooleanField('Remember me')
    submit = SubmitField(_('Log me in!'))
