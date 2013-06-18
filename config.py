import os


class Config(object):
    # ===========================================
    # Flask config
    #
    APP_NAME = 'Flask Boilerplate'
    COMPANY_NAME = 'Flask Boilerplate'
    HOST = '0.0.0.0'
    # Folder where the script runs
    _basedir = os.path.abspath(os.path.dirname(__file__))
    # 2/core TODO: What's this?
    THREADS_PER_PAGE = 8
    # Used if you need to email information to site administrators
    ADMINS = ['stephenvovan@gmail.com']  # TODO
    # Used to sign the cookies; change it and all users will have to login again
    SECRET_KEY = 'SecretKeyForSessionSigning'
    # Debug mode
    DEBUG = False
    # Origins allowed for CORS
    ORIGINS_ALLOWED = ['http://localhost:9000']

    # ===========================================
    # Flask-WTF options
    #
    # Post fraud protection
    CSRF_ENABLED = False
    CSRF_SESSION_KEY = "somethingimpossibletoguess"
    # Settings required to use Recaptcha
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = 'blahblahblahblahblahblahblahblahblah'
    RECAPTCHA_PRIVATE_KEY = 'blahblahblahblahblahblahprivate'
    RECAPTCHA_OPTIONS = {'theme': 'white'}

    # ===========================================
    # Flask-Assets: http://elsdoerfer.name/docs/webassets/environment.html
    #
    # If ASSETS_DEBUG = False, Bundles will be merged and filters applied.
    # If ASSETS_DEBUG = True, Bundles will output their individual source files.
    #ASSETS_DEBUG = False

    # ===========================================
    # Flask-Mail
    #
    MAIL_SERVER = 'email-smtp.us-east-1.amazonaws.com'  # TODO
    MAIL_PORT = 25  # Amazon SES supports 25, 465 or 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = DEBUG
    MAIL_USERNAME = ''  # TODO
    MAIL_PASSWORD = ''  # TODO
    MAIL_DEFAULT_SENDER = 'stephenvovan@gmail.com'  # TODO

    # ===========================================
    # Flask-Babel
    #
    ACCEPT_LANGUAGES = ['en_us', 'fr_ca']
    BABEL_DEFAULT_LOCALE = 'en_us'


class ProdConfig(Config):
    # Flask config
    DEBUG = False
    DOMAIN = 'http://localhost:9000'  # TODO: Change me.
    PORT = int(os.environ.get('PORT', 5000))

    # ===========================================
    # Flask-SQLAlchemy
    #
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')    # TODO: postgres://octopus:C1tizenKan3@localhost/skyfall
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevConfig(Config):
    # ===========================================
    # Flask config
    #
    DEBUG = True
    DOMAIN = 'http://localhost:9000'  # TODO: Change me.
    PORT = int(os.environ.get('PORT', 5000))

    # ===========================================
    # Flask-SQLAlchemy
    #
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config._basedir, 'app.db')
    #DATABASE_CONNECT_OPTIONS = {}  # TODO
    SQLALCHEMY_ECHO = True

    # ===========================================
    # Flask-Mail
    #
    MAIL_FAIL_SILENTLY = True


class TestConfig(Config):
    # ===========================================
    # Flask config
    #
    TESTING = True
    DOMAIN = 'http://localhost:9000'  # TODO: Change me.
    PORT = int(os.environ.get('PORT', 5000))

    # ===========================================
    # Flask-WTF options
    #
    # Post fraud protection
    CSRF_ENABLED = False

    # ===========================================
    # Flask-SQLAlchemy options
    #
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config._basedir, 'test.db')
    SQLALCHEMY_ECHO = False
