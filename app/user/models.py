from flask.ext.login import AnonymousUser
from passlib.hash import sha256_crypt

from app.extensions import db
from app.utils import get_current_time, format_date
from .constants import USER, USER_ROLE, ACTIVE, INACTIVE, USER_STATUS


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(255), unique=True)
    activation_key = db.Column(db.String(36))
    created_time = db.Column(db.DateTime, default=get_current_time)

    # ================================================================
    # Password

    _password = db.Column('password', db.String(20), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = sha256_crypt.encrypt(password, rounds=12345)

    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self._password is None:
            return False
        return sha256_crypt.verify(password, self._password)

    # ================================================================
    # One-to-many relationship between users and roles.
    role_id = db.Column(db.SmallInteger, default=USER)

    def get_role(self):
        return USER_ROLE[self.role_id]

    # ================================================================
    # One-to-many relationship between users and user_statuses.
    status_id = db.Column(db.SmallInteger, default=INACTIVE)

    def get_status(self):
        return USER_STATUS[self.status_id]

    # ================================================================
    # One-to-one (uselist=False) relationship between users and user_details.
    user_detail_id = db.Column(db.Integer, db.ForeignKey("user_details.id"))
    user_detail = db.relationship("UserDetail", uselist=False, backref="users")

    # ================================================================
    # Class methods

    @classmethod  # TODO: What does this do?
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(User.username == login, User.email == login)).first()
        authenticated = user.check_password(password) if user else False

        return user, authenticated

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_dob(self):
        return self.user_detail.dob.isoformat() if self.user_detail.dob is not None else None

    def as_dict(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email,
                "created_time": format_date(self.created_time),
                "first_name": self.user_detail.first_name,
                "last_name": self.user_detail.last_name,
                "gender": self.user_detail.gender,
                "dob": self.get_dob(),
                "phone": self.user_detail.phone,
                "bio": self.user_detail.bio,
                "url": self.user_detail.url
                }

    def session_as_dict(self):
        is_authenticated = self.is_authenticated()
        if (is_authenticated):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email,
                "status": self.get_status(),
                "auth": is_authenticated
            }
        else:
            return {"auth": is_authenticated}

    # ================================================================
    # Required by Flask-Login

    def is_authenticated(self):
        # Should just return True unless the object represents a user that should not be allowed to authenticate for some reason
        return True

    def is_active(self):
        return True if self.status_id == ACTIVE else False

    def is_anonymous(self):
        # Should return True only for fake users that are not supposed to log in to the system.
        return False

    def get_id(self):
        return unicode(self.id)


class Anonymous(AnonymousUser):
    username = u"Anonymous"


class UserDetail(db.Model):

    __tablename__ = 'user_details'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    dob = db.Column(db.Date)
    phone = db.Column(db.String(42))
    bio = db.Column(db.String)
    url = db.Column(db.String)
    created_time = db.Column(db.DateTime, default=get_current_time)
