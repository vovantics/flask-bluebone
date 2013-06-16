import os

from flask import Flask, render_template, request, send_from_directory
from webassets.loaders import PythonLoader as PythonAssetsLoader
import assets
from flaskext.babel import gettext as _

from .extensions import db, mail, login_manager, babel, assets_env
from .user.models import User
from config import DevConfig, ProdConfig, TestConfig
from .utils import format_date

from .meta import meta
from .session import session
from .user import user
DEFAULT_BLUEPRINTS = (
    meta,
    session,
    user
)


def create_app(config=None):
    """Create a Flask app."""

    blueprints = DEFAULT_BLUEPRINTS

    app = Flask(__name__)
    configure_app(app, config)
    configure_hooks(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)

    return app


def configure_app(app, config):
    """Configure app from object, parameter and env."""

    #app.config.from_object(ProdConfig)
    if config is not None:
        app.config.from_object(config)

    # Override setting by env var without touching codes.
    if config is not TestConfig:
        env = os.environ.get('APP_ENV', 'prod')  # {dev, prod}
        app.config.from_object(eval('%sConfig' % env.capitalize()))


def configure_extensions(app):
    # Flask-Assets
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().iteritems():
        assets_env.register(name, bundle)

    # Flask-Babel
    babel.init_app(app)

    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)

    # Flask-SQLAlchemy
    db.init_app(app)

    # Flask-Mail
    mail.init_app(app)

    # Flask-Login
    #login_manager.anonymous_user = Anonymous  TODO
    #login_manager.login_view = "session.login"
    login_manager.login_message = _(u"Please log in to access this page.")
    login_manager.refresh_view = "account.reauth"
    login_manager.needs_refresh_message = (
        _(u"To protect your account, please reauthenticate to access this page.")
    )

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    login_manager.setup_app(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):

    app.jinja_env.filters['format_date'] = format_date
    """@app.template_filter()
    def format_date(value, format='%Y-%m-%d %H:%M:%S'):
        return value.strftime(format)"""


def configure_hooks(app):
    @app.before_request
    def before_request():
        pass


def configure_logging(app):
    """Configure email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode.
        # You can check stdout logging.
        return

    import logging

    # Set info level on logger, which might be overwritten by handlers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    # Error mails
    mail_handler = logging.handlers.SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['MAIL_USERNAME'],
                               app.config['ADMINS'],
                               'Oops... %s failed!' % app.config['APP_NAME'],
                               (app.config['MAIL_USERNAME'],
                                app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(mail_handler)


def configure_error_handlers(app):

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed_page(error):
        return render_template("errors/405.html"), 405

    @app.errorhandler(410)
    def gone(error):
        return render_template("errors/410.html"), 410

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

    @app.route('/robots.txt')
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    @app.route('/sitemap.xml')
    def sitemap():
        url_root = request.url_root[:-1]
        rules = app.url_map.iter_rules()
        return render_template('sitemap.xml', url_root=url_root, rules=rules)
