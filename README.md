# flask-bluebone

flask-bluebone is a REST-ish (it manages session state using cookies) API with CORS support and endpoints for authentication, authorization, registration, profile edit, and password reset/change. Components are loosely coupled. This includes packages (thanks [Blueprints](http://flask.pocoo.org/docs/blueprints/)!), extensions, web assets, and templates.

## Project Structure

    app                      → Application sources
     └ meta                  → Home package
     └ session               → Session package
     └ static                → Asset sources
        └ css                → Typically LESS CSS sources
           └ email           → Email styles
           └ error           → Error styles
        └ public             → Public assets
           └ css             → CSS files
     └ templates             → Templates
     └ translations          → Translation template and translation files
     └ user                  → User package
      __init__.py            → App initialization
      assets.py              → Flask-Assets config
      babel.cfg              → Flask-Babel config
      constants.py           → Global constants
      extensions.py          → Flask extensions instantiated here
      utils.py               → Global utilities
    .gitignore               → Untracked files that git should ignore
    .slugignore              → Untracked files that heroku should ignore
    Procfile                 → Command to executed by Heroku to start a web dyno
    README.md                → Used for Readme Driven Development
    config.py                → Flask configuration module
    fabfile.py               → Fabric tasks
    manage.py                → Flask-Script tasks
    setup.py                 → Fabric setup code
    tests.py                 → Tests module

## Flask

kennethreitz's [flasky-goodness](https://speakerdeck.com/kennethreitz/flasky-goodness) presentation is a good explanation of why Flask rules.

### [Flask-Assets](http://elsdoerfer.name/docs/flask-assets/)

Transactional emails and error pages are styled with CSS. These assets are compiled and minified with Flask-Assets. [cssmin](https://npmjs.org/package/cssmin) is used for minifying. Source stylesheet categorization, naming convention, and formatting follows [SMACSS](http://smacss.com/).

### [Flask-Babel](http://packages.python.org/Flask-Babel/)

i18n and l10n support is provided by Flask-Babel.

### [Flask-Login](http://packages.python.org/Flask-Login/)

User session management built on top of Flask-Login and [passlib](http://pypi.python.org/pypi/passlib). This includes authentication, registration, and password reset/change.

### [Flask-Mail](https://github.com/mattupstate/flask-mail)

[Gmail doesn't support style tags in HTML emails](http://www.campaignmonitor.com/css/). Inline style attributes must be defined on the DOM element.
The [premailer](https://pypi.python.org/pypi/premailer/) package parses an HTML page containing style blocks, parses the CSS, and yields an HTML string with inline style attributes. This is used for transactional emails. The emails are sent using Flask-Mail's SMTP support.

### [Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/)

There's not out of the box support for any database with Flask. The Flask-SQLAlchemy extension provides an excellent database toolkit and ORM.

### [Flask-Script](http://flask-script.readthedocs.org/en/latest/index.html)

Flask-Script provides commands to run the Flask development server, open a Python shell, create DB, drop DB, init DB) from the terminal.

### [Flask-WTF](http://pythonhosted.org/Flask-WTF/)

Flask-WTF offers integration with [WTForms](http://wtforms.simplecodes.com/docs/dev/). This API uses WTForms for validating AJAX POST and PUT requests. Flask-WTF also includes CSRF protection. An API precludes CSRF, because its purpose is generally to allow 3rd-party entities to access and manipulate data on your site (the "cross-site" in CSRF). Therefore, CSRF protection is disabled.

## Testing

Unit tests are written using [unittest](http://docs.python.org/library/unittest.html) + [Flask-Testing](http://packages.python.org/Flask-Testing/). Tests are run with [nose](http://nose.readthedocs.org/en/latest/) and its [coverage](http://nedbatchelder.com/code/coverage/) plugin.

## Workflows

### Install

* Git

        $ sudo apt-get install git-core

* [pip](https://python-guide.readthedocs.org/en/latest/)
* [Python and Virtualenv](http://install.python-guide.org/)

* fabric

        $ pip install fabric

* [s3cmd](http://s3tools.org/s3cmd) for syncing web assets with Amazon S3

        $ sudo apt-get install s3cmd
        $ s3cmd --configure

* [cloc](http://cloc.sourceforge.net/) for counting LOC

        $ sudo apt-get install cloc

1. Clone this repo

        $ git clone git://github.com/vovantics/flask-bluebone.git
        $ cd flask-bluebone

1. Create and activate virtual environment

        $ virtualenv venv --distribute --no-site-packages
        $ source venv/bin/activate

1. Setup

        $ fab setup

### Development process

1. Build web assets

        $ ./manage.py assets build

1. Set app environment to dev (do this once)

        $ export APP_ENV=dev

1. Start Flask server

        $ fab run

1. Open the app in your browser

    [http://127.0.0.1:5000/users/me/](http://127.0.0.1:5000/users/me/)

## Test process

    $ fab test

## Deployment process

Deploying with [Fabric](http://flask.pocoo.org/docs/patterns/fabric/).

Based on the [Getting Started with Python on Heroku](http://devcenter.heroku.com/articles/python).

Anything written to standard out (stdout) or standard error (stderr) is captured into your heroku logs. Error mails are sent the second the exception happens using Flask's native [logging handlers](http://flask.pocoo.org/docs/errorhandling/)


Prerequisites:

1. Install the [Heroku Toolbelt](https://toolbelt.heroku.com/) on your local workstation

1. Login to the Heroku CLI tool

        $ heroku login

1. Create a new application on Heroku.

        $ heroku create -s cedar






1. Deploy your code

        $ git push heroku master

1. Create database schema

        $ heroku run "python manage.py initdb"

1. Open the app in your browser

        $ heroku open

1. Verify that it works

1. Set the concurrency level to one web dyno

        $ heroku ps:scale web=1

## TODO

* Dynamic documentation using Sphinx

## Acknowledgements

* Armin Ronacher's [how-to large project structure with flask and some basic modules](https://github.com/mitsuhiko/flask/wiki/Large-app-how-to)
* The traveling coder's guide on [Building websites in Python with Flask](http://maximebf.com/blog/2012/10/building-websites-in-python-with-flask)
* [HTML EMAIL BOILERPLATE](http://htmlemailboilerplate.com/)
* [Patterns for Flask](http://flask.pocoo.org/docs/patterns/)
* imwilsonxu's [fbone](https://github.com/imwilsonxu/fbone)