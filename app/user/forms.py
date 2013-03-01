from flask.ext.wtf import Form, Required, EqualTo, Length, Email, \
URL
from flask.ext.wtf import TextField, PasswordField, TextAreaField, \
DateField, SelectField, SubmitField
from flask.ext.wtf.html5 import EmailField, TelField, URLField
from flaskext.babel import gettext as _
from .constants import (FIRSTNAME_LEN_MIN, FIRSTNAME_LEN_MAX, \
    LASTNAME_LEN_MIN, LASTNAME_LEN_MAX, PASSWORD_LEN_MIN, \
    PASSWORD_LEN_MAX, USERNAME_LEN_MIN, USERNAME_LEN_MAX)


class ActivateForm(Form):
    status = TextField(_('Status'), [Required()])


class ChangePasswordForm(Form):
    password = PasswordField(
        label=_('New password'),
        validators=[
            Required(message=_('New password is required')),
            Length(
                min=PASSWORD_LEN_MIN,
                max=PASSWORD_LEN_MAX,
                )
            ]
        )
    password_again = PasswordField(
        label=_('New password again'),
        validators=[
            EqualTo('password', message=_("Passwords don't match."))
            ]
        )
    submit = SubmitField(_('Change Password'))


class DeactivateAccountForm(Form):
    submit = SubmitField(_("I'd like to delete my account"))


class ProfileForm(Form):
    first_name = TextField(
        label=_('First Name'),
        validators=[
            Length(
                min=FIRSTNAME_LEN_MIN,
                max=FIRSTNAME_LEN_MAX,
                ),
            ],
        )
    last_name = TextField(
        label=_('Last Name'),
        validators=[
            Length(
                min=LASTNAME_LEN_MIN,
                max=LASTNAME_LEN_MAX,
                ),
            ],
        )
    username = TextField(
        label=_('Username'),
        validators=[
            Required(),
            Length(
                min=USERNAME_LEN_MIN,
                max=USERNAME_LEN_MAX,
                ),
            ],
        description=_(u"Combination of letters/digits/underscore, at least %s characters." % USERNAME_LEN_MIN),
        )
    email = EmailField(
        label=_('Email'),
        validators=[Email(
            message=_("Doesn't look like a valid email.")
            )],
        )
    """ TODO role_id = RadioField(
        label=_('Role'),
        validators=[
            validators.AnyOf(USER_ROLE.keys())
            ],
        choices=USER_ROLE.items(),
        )"""
    gender = SelectField(
        label=_('Gender'),
        choices=[
            ('male', 'Male'),
            ('female', 'Female')
            ]
        )
    dob = DateField(
        label=_('Date of Birth')
        )
    phone = TelField(
        label=_('Phone Number'),
        )
    bio = TextAreaField(
        label=_('Biography'),
        validators=[
            Length(
                max=1024,
                ),
            ]
        )
    url = URLField(
        label=_('Website'),
        validators=[
            URL(),
            ],
        )
    submit = SubmitField(_('Save'))


class RecoverPasswordForm(Form):
    email = EmailField(
        label=_('Your email'),
        validators=[
            Email(message=_("That doesn't look like an email."))
            ]
        )
    submit = SubmitField(_('Send instructions'))


class RegisterForm(Form):
    username = TextField(
        label=_('Username'),
        validators=[
            Required()
            ]
        )
    email = EmailField(
        label=_('Email address'),
        validators=[
            Required(),
            Email("That doesn't look like an email.")
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
    password_again = PasswordField(
        label=_('Repeat Password'),
        validators=[
            Required(),
            EqualTo('password_again', message=_('Passwords must match.'))
            ]
        )
    #recaptcha = RecaptchaField()
    submit = SubmitField(_('Create account'))
